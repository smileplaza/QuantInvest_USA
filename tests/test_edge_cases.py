"""
엣지 케이스 및 방어 로직 테스트

극단적 파라미터, 초단기/빈 데이터, 거래량 0, 최적화 전체 실패 등
비정상 입력에서 애플리케이션이 크래시하지 않고 명확한 예외 또는
안전한 기본값을 반환하는지 검증한다.
"""

import numpy as np
import pandas as pd
import pytest

from strategies.base_strategy import BaseStrategy, InsufficientDataError
from strategies.momentum_strategy import MomentumStrategy
from strategies.trend_following import TrendFollowingStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.portfolio import PortfolioStrategy
from backtest.engine import BacktestEngine
from backtest.metrics import MetricsCalculator


class TestExtremeParameters:
    """데이터 길이를 초과하는 극단적 파라미터"""

    def test_mean_reversion_lookback_exceeds_length(self, short_data):
        # short_data는 60행. lookback 100 → 롤링 후 전부 NaN → dropna → 빈 데이터
        strat = MeanReversionStrategy()
        strat.params = {'lookback_period': 100, 'z_score_threshold': 1.96, 'position_size': 0.5}
        signals = strat.calculate_signals(short_data)
        with pytest.raises(InsufficientDataError):
            strat.run_backtest(signals)

    def test_momentum_period_exceeds_length(self, short_data):
        # momentum_period 100 > 60행 → pct_change 전부 NaN → dropna → 빈 데이터
        strat = MomentumStrategy()
        strat.params = {'momentum_period': 100, 'mfi_period': 7, 'mfi_level': 46.5, 'stop_loss': 0.07}
        signals = strat.calculate_signals(short_data)
        with pytest.raises(InsufficientDataError):
            strat.run_backtest(signals)

    def test_engine_surfaces_insufficient_data(self, short_data):
        # 엔진을 통해 실행해도 동일 예외가 전파되어야 함 (크래시 아님)
        strat = MeanReversionStrategy()
        strat.params = {'lookback_period': 200, 'z_score_threshold': 1.96, 'position_size': 0.5}
        engine = BacktestEngine()
        with pytest.raises(InsufficientDataError):
            engine.run_strategy(strat, short_data)


class TestVeryShortData:
    """단일/초단기 데이터"""

    def test_single_row_raises(self, make_ohlcv):
        data = make_ohlcv(n=1, seed=1)
        strat = TrendFollowingStrategy()
        signals = strat.calculate_signals(data)
        with pytest.raises(InsufficientDataError):
            strat.run_backtest(signals)

    def test_two_rows_does_not_crash(self, make_ohlcv):
        # 최소 행 수(2)에서는 크래시 없이 결과를 반환해야 함
        data = make_ohlcv(n=2, seed=2)
        strat = TrendFollowingStrategy()
        signals = strat.calculate_signals(data)
        result = strat.run_backtest(signals)
        assert 'Cumulative_Return' in result.columns
        assert len(result) == 2


class TestZeroVolume:
    """거래량이 모두 0인 데이터"""

    def test_momentum_zero_volume_no_unhandled_crash(self, make_ohlcv):
        data = make_ohlcv(n=120, seed=5)
        data['Volume'] = 0  # 전 구간 거래량 0

        strat = MomentumStrategy()
        engine = BacktestEngine()
        # MFI가 NaN이 되어 InsufficientDataError가 나거나,
        # 유효 데이터가 남아 정상 지표를 반환하거나 — 어느 쪽이든 크래시는 없어야 함
        try:
            result = engine.run_strategy(strat, data)
            assert 'metrics' in result
        except InsufficientDataError:
            pass  # 허용되는 방어적 예외


class TestExtremeStopLoss:
    """극단적인 손절 값"""

    def test_zero_stop_loss(self, sample_data):
        strat = TrendFollowingStrategy()
        strat.params = {'short_window': 12, 'long_window': 26, 'stop_loss': 0.0}
        engine = BacktestEngine()
        result = engine.run_strategy(strat, sample_data)
        assert np.isfinite(result['metrics']['cagr'])

    def test_full_stop_loss(self, sample_data):
        # stop_loss=1.0 (100%) 는 사실상 손절 미발동
        strat = TrendFollowingStrategy()
        strat.params = {'short_window': 12, 'long_window': 26, 'stop_loss': 1.0}
        engine = BacktestEngine()
        result = engine.run_strategy(strat, sample_data)
        assert np.isfinite(result['metrics']['cagr'])


class TestOptimizationAllFail:
    """모든 파라미터 조합이 실패하는 경우"""

    def test_all_combinations_fail_raises(self, short_data):
        # 60행 데이터에 lookback 100~110 → 모든 조합이 빈 데이터 유발
        strat = MeanReversionStrategy()
        param_ranges = {
            'lookback_period': (100, 110, 5),
            'z_score_threshold': (1.96, 1.96, 1),
            'position_size': (0.5, 0.5, 1),
        }
        with pytest.raises(InsufficientDataError):
            strat.optimize_parameters(short_data, param_ranges)


class TestMetricsRobustness:
    """지표 계산 방어 로직"""

    def test_empty_dataframe_returns_zero_metrics(self):
        calc = MetricsCalculator()
        empty = pd.DataFrame()
        metrics = calc.calculate_all_metrics(empty, initial_capital=10000)
        assert metrics['cagr'] == 0.0
        assert metrics['total_trades'] == 0
        assert len(metrics) == 10

    def test_missing_cumret_column_returns_zero_metrics(self):
        calc = MetricsCalculator()
        data = pd.DataFrame({'Close': [100, 101, 102]})
        metrics = calc.calculate_all_metrics(data, initial_capital=10000)
        assert metrics['cagr'] == 0.0

    def test_cagr_short_period_no_overflow(self):
        # 2행(≈0.008년)에 큰 수익률 → 연율화 시 오버플로 위험. 유한값이어야 함
        cagr = MetricsCalculator.calculate_cagr(cumulative_return=1.5, years=2 / 252)
        assert np.isfinite(cagr)

    def test_cagr_continuity_at_one_year(self):
        # years=1.0 경계에서 기존 공식과 연속인지 확인
        just_under = MetricsCalculator.calculate_cagr(0.5, 0.999)
        at_one = MetricsCalculator.calculate_cagr(0.5, 1.0)
        assert at_one == pytest.approx(0.5, rel=1e-6)
        assert just_under == pytest.approx(0.5, rel=1e-2)


class TestConstantPrice:
    """가격 변동이 전혀 없는 데이터 (변동성 0)"""

    def test_flat_price_no_crash(self, make_ohlcv):
        data = make_ohlcv(n=100, seed=9)
        # 모든 가격을 동일하게 고정
        for col in ['Open', 'High', 'Low', 'Close']:
            data[col] = 100.0

        strat = TrendFollowingStrategy()
        engine = BacktestEngine()
        result = engine.run_strategy(strat, data)
        # 변동성 0 → 샤프 0, 모든 지표 유한
        assert result['metrics']['sharpe_ratio'] == 0.0
        assert np.isfinite(result['metrics']['cagr'])
