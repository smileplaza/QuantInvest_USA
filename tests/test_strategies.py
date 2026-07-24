"""
전략 구현 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from strategies.base_strategy import BaseStrategy
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
class TestStrategyInterface:
    """모든 전략이 공통 인터페이스를 준수하는지 검증"""

    def test_inherits_base(self, strategy_cls):
        assert issubclass(strategy_cls, BaseStrategy)

    def test_default_construction(self, strategy_cls):
        strategy = strategy_cls()
        assert strategy.initial_capital == 10000
        assert strategy.transaction_fee == 0.001
        assert isinstance(strategy.params, dict)
        assert len(strategy.params) > 0

    def test_calculate_signals_adds_signal_column(self, strategy_cls, sample_data):
        strategy = strategy_cls()
        result = strategy.calculate_signals(sample_data)
        assert "Signal" in result.columns

    def test_signal_values_are_valid(self, strategy_cls, sample_data):
        strategy = strategy_cls()
        result = strategy.calculate_signals(sample_data)
        valid = {-1.0, 0.0, 1.0}
        assert set(result["Signal"].unique()).issubset(valid)

    def test_run_backtest_adds_cumulative_return(self, strategy_cls, sample_data):
        strategy = strategy_cls()
        signals = strategy.calculate_signals(sample_data)
        result = strategy.run_backtest(signals)
        assert "Cumulative_Return" in result.columns
        assert "Portfolio_Value" in result.columns

    def test_backtest_does_not_mutate_input(self, strategy_cls, sample_data):
        strategy = strategy_cls()
        signals = strategy.calculate_signals(sample_data)
        before = signals.copy(deep=True)
        strategy.run_backtest(signals)
        pd.testing.assert_frame_equal(signals, before)

    def test_cumulative_return_starts_at_one(self, strategy_cls, sample_data):
        strategy = strategy_cls()
        signals = strategy.calculate_signals(sample_data)
        result = strategy.run_backtest(signals)
        # 초기 포트폴리오 가치는 초기 자본과 동일 → 누적 수익률 1.0
        assert result["Cumulative_Return"].iloc[0] == pytest.approx(1.0)

    def test_portfolio_value_non_negative(self, strategy_cls, sample_data):
        strategy = strategy_cls()
        signals = strategy.calculate_signals(sample_data)
        result = strategy.run_backtest(signals)
        assert (result["Portfolio_Value"] >= 0).all()


class TestMomentumStrategy:
    """모멘텀 전략 특화 테스트"""

    def test_mfi_computed_with_volume(self, sample_data):
        strategy = MomentumStrategy()
        result = strategy.calculate_signals(sample_data)
        assert "MFI" in result.columns
        # MFI는 0-100 범위
        assert result["MFI"].between(0, 100).all()

    def test_momentum_column_present(self, sample_data):
        strategy = MomentumStrategy()
        result = strategy.calculate_signals(sample_data)
        assert "Momentum" in result.columns

    def test_repr(self):
        strategy = MomentumStrategy()
        text = repr(strategy)
        assert "MomentumStrategy" in text


class TestTrendFollowingStrategy:
    """추세 추종 전략 특화 테스트"""

    def test_ema_columns(self, sample_data):
        strategy = TrendFollowingStrategy()
        result = strategy.calculate_signals(sample_data)
        assert "Short_EMA" in result.columns
        assert "Long_EMA" in result.columns

    def test_short_ema_more_reactive(self, sample_data):
        strategy = TrendFollowingStrategy()
        result = strategy.calculate_signals(sample_data)
        # 단기 EMA의 변동성이 장기 EMA보다 큼
        assert result["Short_EMA"].std() >= result["Long_EMA"].std() * 0.5


class TestMeanReversionStrategy:
    """평균 회귀 전략 특화 테스트"""

    def test_zscore_column(self, sample_data):
        strategy = MeanReversionStrategy()
        result = strategy.calculate_signals(sample_data)
        assert "Z_Score" in result.columns

    def test_zscore_roughly_centered(self, flat_data):
        strategy = MeanReversionStrategy()
        result = strategy.calculate_signals(flat_data)
        # Z-점수는 평균 0 근처
        assert abs(result["Z_Score"].mean()) < 1.0


class TestOptimization:
    """파라미터 최적화 테스트"""

    def test_trend_following_optimization(self, sample_data):
        strategy = TrendFollowingStrategy()
        param_ranges = {
            "short_window": (5, 15, 5),
            "long_window": (20, 30, 5),
            "stop_loss": (0.05, 0.10, 0.05),
        }
        best_params, best_return = strategy.optimize_parameters(sample_data, param_ranges)
        assert best_params is not None
        assert "short_window" in best_params
        assert isinstance(best_return, float)

    def test_generate_combinations_count(self):
        param_ranges = {
            "a": (1, 3, 1),  # 1, 2, 3 → 3개
            "b": (10, 20, 5),  # 10, 15, 20 → 3개
        }
        combos = BaseStrategy._generate_combinations(param_ranges)
        assert len(combos) == 9  # 3 x 3
