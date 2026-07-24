"""
성능 지표 계산 단위 테스트
"""

import numpy as np
import pandas as pd
import pytest

from backtest.metrics import MetricsCalculator


class TestCAGR:
    """연평균 성장률 계산 테스트"""

    def test_doubling_over_one_year(self):
        # 누적 수익률 1.0 (즉 100% 수익 = 2배), 1년
        cagr = MetricsCalculator.calculate_cagr(cumulative_return=1.0, years=1.0)
        assert cagr == pytest.approx(1.0, rel=1e-6)

    def test_quadruple_over_two_years(self):
        # 누적 수익률 3.0 (4배), 2년 → 연 100%
        cagr = MetricsCalculator.calculate_cagr(cumulative_return=3.0, years=2.0)
        assert cagr == pytest.approx(1.0, rel=1e-6)

    def test_zero_years_returns_zero(self):
        assert MetricsCalculator.calculate_cagr(1.0, 0.0) == 0.0

    def test_negative_return_returns_zero(self):
        # 음수 누적 수익률은 0 반환 (구현 방어 로직)
        assert MetricsCalculator.calculate_cagr(-0.5, 1.0) == 0.0


class TestMaxDrawdown:
    """최대 낙폭 계산 테스트"""

    def test_known_drawdown(self):
        # 100 → 120 → 60 → 90, 최대 낙폭은 120 기준 60까지 = -50%
        series = pd.Series([100, 120, 60, 90], dtype=float)
        mdd = MetricsCalculator.calculate_max_drawdown(series)
        assert mdd == pytest.approx(-0.5, rel=1e-6)

    def test_monotonic_increase_no_drawdown(self):
        series = pd.Series([100, 110, 120, 130], dtype=float)
        mdd = MetricsCalculator.calculate_max_drawdown(series)
        assert mdd == pytest.approx(0.0, abs=1e-9)


class TestSharpeRatio:
    """샤프 지수 계산 테스트"""

    def test_zero_volatility_returns_zero(self):
        calc = MetricsCalculator()
        returns = pd.Series([0.0, 0.0, 0.0, 0.0])
        assert calc.calculate_sharpe_ratio(returns) == 0.0

    def test_positive_returns_positive_sharpe(self):
        calc = MetricsCalculator()
        # 일관되게 소폭 상승하는 수익률
        rng = np.random.default_rng(0)
        returns = pd.Series(rng.normal(0.001, 0.005, 252))
        sharpe = calc.calculate_sharpe_ratio(returns)
        assert sharpe > 0


class TestCalmarRatio:
    """칼마 비율 계산 테스트"""

    def test_normal_case(self):
        # CAGR 20%, MDD -10% → 칼마 2.0
        calmar = MetricsCalculator.calculate_calmar_ratio(cagr=0.20, max_drawdown=-0.10)
        assert calmar == pytest.approx(2.0, rel=1e-6)

    def test_zero_drawdown_returns_zero(self):
        assert MetricsCalculator.calculate_calmar_ratio(0.20, 0.0) == 0.0


class TestTradeMetrics:
    """거래 기반 지표 테스트"""

    def _make_signal_frame(self):
        # 매수(1) → 매도(-1) 사이클을 갖는 프레임
        idx = pd.date_range("2022-01-01", periods=6, freq="D")
        return pd.DataFrame(
            {
                "Close": [100, 105, 110, 108, 95, 100],
                "Signal": [0, 1, 0, -1, 1, -1],
            },
            index=idx,
        )

    def test_total_trades(self):
        data = self._make_signal_frame()
        # 매수 2회, 매도 2회 → min = 2
        assert MetricsCalculator.calculate_total_trades(data) == 2

    def test_winning_and_losing(self):
        data = self._make_signal_frame()
        # 첫 거래: 105 매수 → 108 매도 (이익)
        # 둘째 거래: 95 매수 → 100 매도 (이익)
        winning = MetricsCalculator.calculate_winning_trades(data)
        losing = MetricsCalculator.calculate_losing_trades(data)
        assert winning + losing == MetricsCalculator.calculate_total_trades(data)

    def test_win_rate_range(self):
        data = self._make_signal_frame()
        rate = MetricsCalculator.calculate_win_rate(data)
        assert 0.0 <= rate <= 1.0

    def test_missing_signal_column_returns_zero(self):
        data = pd.DataFrame({"Close": [100, 101, 102]})
        assert MetricsCalculator.calculate_total_trades(data) == 0
        assert MetricsCalculator.calculate_win_rate(data) == 0.0


class TestCalculateAllMetrics:
    """전체 지표 통합 계산 테스트"""

    def test_all_metrics_present(self):
        idx = pd.date_range("2022-01-01", periods=252, freq="B")
        cumret = pd.Series(np.linspace(1.0, 1.5, 252), index=idx)
        data = pd.DataFrame(
            {
                "Close": np.linspace(100, 150, 252),
                "Cumulative_Return": cumret,
                "Signal": 0.0,
            },
            index=idx,
        )
        calc = MetricsCalculator()
        metrics = calc.calculate_all_metrics(data, initial_capital=10000)
        assert len(metrics) == 10
        assert metrics["cagr"] > 0
