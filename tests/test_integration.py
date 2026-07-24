"""
엔드투엔드 통합 테스트
데이터 → 전략 → 백테스트 → 지표 → 최적화 전체 워크플로 검증
"""

import pandas as pd
import pytest

from backtest.engine import BacktestEngine
from data.cache import CacheManager
from strategies.momentum_strategy import MomentumStrategy
from strategies.trend_following import TrendFollowingStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.portfolio import PortfolioStrategy

ALL_STRATEGIES = [
    MomentumStrategy,
    TrendFollowingStrategy,
    MeanReversionStrategy,
    PortfolioStrategy,
]


@pytest.mark.parametrize("strategy_cls", ALL_STRATEGIES)
def test_full_backtest_workflow(strategy_cls, sample_data):
    """모든 전략에 대해 전체 백테스트 워크플로가 완주하는지 검증"""
    engine = BacktestEngine()
    result = engine.run_strategy(strategy_cls(), sample_data)

    assert result["metrics"] is not None
    assert "Cumulative_Return" in result["data"].columns
    # 지표 값들이 숫자형인지 확인
    metrics = result["metrics"]
    assert isinstance(metrics["cagr"], float)
    assert isinstance(metrics["total_trades"], int)


def test_cache_to_backtest_workflow(tmp_path, sample_data):
    """캐시에 저장 → 조회 → 백테스트 실행 통합"""
    db_path = tmp_path / "integration.db"
    cache = CacheManager(db_path=str(db_path))

    # 저장
    cache.store_data("TEST", sample_data)

    # 전체 범위 조회
    start = sample_data.index[0].strftime("%Y-%m-%d")
    end = sample_data.index[-1].strftime("%Y-%m-%d")
    cached = cache.get_data("TEST", start, end)

    assert cached is not None
    assert len(cached) == len(sample_data)

    # 캐시에서 가져온 데이터로 백테스트
    engine = BacktestEngine()
    result = engine.run_strategy(TrendFollowingStrategy(), cached)
    assert result["metrics"] is not None


def test_optimization_workflow(sample_data):
    """최적화 → 최적 파라미터로 백테스트 통합"""
    engine = BacktestEngine()
    strategy = TrendFollowingStrategy()

    param_ranges = {
        "short_window": (5, 15, 5),
        "long_window": (20, 30, 5),
        "stop_loss": (0.05, 0.10, 0.05),
    }

    opt_result = engine.run_optimization(strategy, sample_data, param_ranges)
    assert opt_result["optimal_params"] is not None

    # 최적 파라미터로 재실행
    strategy.params = opt_result["optimal_params"]
    final = engine.run_strategy(strategy, sample_data)
    assert final["metrics"] is not None


def test_strategy_comparison_workflow(sample_data):
    """여러 전략을 한 번에 비교"""
    engine = BacktestEngine()
    strategies = [cls() for cls in ALL_STRATEGIES]
    results = engine.compare_strategies(strategies, sample_data)

    assert len(results) == len(ALL_STRATEGIES)
    for name, metrics in results.items():
        assert "cagr" in metrics
