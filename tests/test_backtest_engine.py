"""
백테스팅 엔진 단위 테스트
"""

import pandas as pd
import pytest

from backtest.engine import BacktestEngine
from strategies.base_strategy import BaseStrategy
from strategies.trend_following import TrendFollowingStrategy
from strategies.momentum_strategy import MomentumStrategy


class TestBacktestEngine:
    """백테스트 엔진 실행 테스트"""

    def test_run_strategy_returns_expected_keys(self, sample_data):
        engine = BacktestEngine()
        result = engine.run_strategy(TrendFollowingStrategy(), sample_data)
        assert "data" in result
        assert "metrics" in result
        assert "strategy" in result

    def test_metrics_contains_all_fields(self, sample_data):
        engine = BacktestEngine()
        result = engine.run_strategy(TrendFollowingStrategy(), sample_data)
        metrics = result["metrics"]
        for field in [
            "cagr",
            "sharpe_ratio",
            "max_drawdown",
            "win_rate",
            "profit_loss_ratio",
            "total_trades",
            "winning_trades",
            "losing_trades",
            "avg_holding_period",
            "calmar_ratio",
        ]:
            assert field in metrics

    def test_custom_capital_propagates(self, sample_data):
        engine = BacktestEngine(initial_capital=50000)
        result = engine.run_strategy(TrendFollowingStrategy(initial_capital=50000), sample_data)
        assert result["data"]["Portfolio_Value"].iloc[0] == pytest.approx(50000)

    def test_compare_strategies(self, sample_data):
        engine = BacktestEngine()
        strategies = [TrendFollowingStrategy(), MomentumStrategy()]
        results = engine.compare_strategies(strategies, sample_data)
        assert "TrendFollowingStrategy" in results
        assert "MomentumStrategy" in results

    def test_generate_report_contains_metrics(self, sample_data):
        engine = BacktestEngine()
        result = engine.run_strategy(TrendFollowingStrategy(), sample_data)
        report = engine.generate_report(result)
        assert "백테스트 결과 보고서" in report
        assert "CAGR" in report

    def test_generate_report_writes_file(self, sample_data, tmp_path):
        engine = BacktestEngine()
        result = engine.run_strategy(TrendFollowingStrategy(), sample_data)
        out = tmp_path / "report.txt"
        engine.generate_report(result, output_path=str(out))
        assert out.exists()
        assert "CAGR" in out.read_text(encoding="utf-8")


class TestBuySellExecution:
    """매수/매도 실행 로직 테스트"""

    def test_execute_buy_respects_fee(self):
        strategy = TrendFollowingStrategy()
        shares, remaining = strategy._execute_buy(price=100, cash=10000, fee_rate=0.001)
        # 수수료 포함 총 비용이 현금을 초과하지 않음
        assert shares * 100 * 1.001 <= 10000 + 1e-6
        assert remaining >= 0

    def test_execute_sell_deducts_fee(self):
        strategy = TrendFollowingStrategy()
        proceeds = strategy._execute_sell(price=100, shares=10, fee_rate=0.001)
        # 매도 대금 = 100 * 10 * (1 - 0.001) = 999
        assert proceeds == pytest.approx(999.0)

    def test_buy_then_sell_roundtrip_with_fees_loses_value(self):
        """수수료 때문에 즉시 매수 후 매도하면 손실"""
        strategy = TrendFollowingStrategy()
        shares, remaining = strategy._execute_buy(price=100, cash=10000, fee_rate=0.001)
        proceeds = strategy._execute_sell(price=100, shares=shares, fee_rate=0.001)
        assert remaining + proceeds < 10000


class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_short_data(self, short_data):
        engine = BacktestEngine()
        result = engine.run_strategy(TrendFollowingStrategy(), short_data)
        assert result["metrics"] is not None

    def test_no_trades_scenario(self, sample_data):
        """신호가 전혀 없어도 크래시하지 않음"""

        class NoSignalStrategy(BaseStrategy):
            def calculate_signals(self, data):
                data = data.copy()
                data["Signal"] = 0.0
                return data

            def run_backtest(self, data):
                data = data.copy()
                data["Portfolio_Value"] = self.initial_capital
                data["Cumulative_Return"] = 1.0
                return data

        engine = BacktestEngine()
        result = engine.run_strategy(NoSignalStrategy(), sample_data)
        assert result["metrics"]["total_trades"] == 0
