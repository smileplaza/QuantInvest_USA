"""
성능 지표 계산 모듈
"""

import pandas as pd
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """성능 지표 계산 클래스"""

    def __init__(self, risk_free_rate: float = 0.003):
        """
        계산기 초기화

        Args:
            risk_free_rate (float): 무위험 이율 (기본값: 0.3% 연율)
        """
        self.risk_free_rate = risk_free_rate

    # 지표 계산 실패 시 반환하는 기본값 (모든 필드 0)
    _ZERO_METRICS = {
        'cagr': 0.0, 'sharpe_ratio': 0.0, 'max_drawdown': 0.0,
        'win_rate': 0.0, 'profit_loss_ratio': 0.0, 'total_trades': 0,
        'winning_trades': 0, 'losing_trades': 0, 'avg_holding_period': 0.0,
        'calmar_ratio': 0.0,
    }

    def calculate_all_metrics(self, data: pd.DataFrame, initial_capital: float) -> Dict:
        """
        모든 성능 지표 계산

        Args:
            data (pd.DataFrame): 백테스트 결과 데이터
            initial_capital (float): 초기 자본

        Returns:
            Dict: 모든 지표
        """
        # 빈 데이터 또는 필수 열 누락 시 0 지표 반환 (크래시 방지)
        if data is None or len(data) == 0 or 'Cumulative_Return' not in data.columns:
            logger.warning("지표 계산: 데이터가 비어 있거나 Cumulative_Return 열이 없습니다.")
            return dict(self._ZERO_METRICS)

        cumulative_returns = data['Cumulative_Return']
        returns_series = cumulative_returns.pct_change().fillna(0)

        # 투자 기간 (연도)
        trading_days = len(data)
        years = trading_days / 252.0

        return {
            'cagr': self.calculate_cagr(cumulative_returns.iloc[-1], years),
            'sharpe_ratio': self.calculate_sharpe_ratio(returns_series),
            'max_drawdown': self.calculate_max_drawdown(cumulative_returns),
            'win_rate': self.calculate_win_rate(data),
            'profit_loss_ratio': self.calculate_profit_loss_ratio(data),
            'total_trades': self.calculate_total_trades(data),
            'winning_trades': self.calculate_winning_trades(data),
            'losing_trades': self.calculate_losing_trades(data),
            'avg_holding_period': self.calculate_avg_holding_period(data),
            'calmar_ratio': self.calculate_calmar_ratio(
                self.calculate_cagr(cumulative_returns.iloc[-1], years),
                self.calculate_max_drawdown(cumulative_returns)
            )
        }

    @staticmethod
    def calculate_cagr(cumulative_return: float, years: float) -> float:
        """연평균 성장률 (CAGR) 계산.

        투자 기간이 1년 미만으로 매우 짧으면 연율화(annualization) 시 값이
        비현실적으로 커지거나 오버플로(inf)가 발생할 수 있다. 이 경우 연율화하지
        않고 기간 전체 수익률을 그대로 반환한다. years=1.0에서 기존 공식
        `(1+r)**(1/years) - 1`과 정확히 연속(둘 다 r 반환)이므로 안전하다.
        """
        if years <= 0 or cumulative_return < 0:
            return 0.0

        if years < 1.0:
            # 1년 미만은 연율화 왜곡을 피하기 위해 총 수익률을 그대로 사용
            result = cumulative_return
        else:
            result = (1 + cumulative_return) ** (1 / years) - 1

        # 오버플로/비유한 값 방어
        if not np.isfinite(result):
            return 0.0
        return result

    def calculate_sharpe_ratio(self, returns_series: pd.Series) -> float:
        """샤프 지수 계산"""
        mean_return = returns_series.mean() * 252
        std_return = returns_series.std() * np.sqrt(252)

        if std_return == 0:
            return 0.0

        return (mean_return - self.risk_free_rate) / std_return

    @staticmethod
    def calculate_max_drawdown(cumulative_returns: pd.Series) -> float:
        """최대 낙폭 (MDD) 계산"""
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        return drawdown.min()

    @staticmethod
    def calculate_win_rate(data: pd.DataFrame) -> float:
        """승률 계산"""
        if 'Signal' not in data.columns:
            return 0.0

        buy_signals = data[data['Signal'] == 1].index
        sell_signals = data[data['Signal'] == -1].index

        profitable_trades = 0
        total_trades = 0

        for buy_idx in buy_signals:
            sell_after = sell_signals[sell_signals > buy_idx]
            if len(sell_after) > 0:
                sell_idx = sell_after[0]
                buy_price = data.loc[buy_idx, 'Close']
                sell_price = data.loc[sell_idx, 'Close']

                if sell_price > buy_price:
                    profitable_trades += 1

                total_trades += 1

        if total_trades == 0:
            return 0.0

        return profitable_trades / total_trades

    @staticmethod
    def calculate_profit_loss_ratio(data: pd.DataFrame) -> float:
        """수익/손실 비율 계산"""
        if 'Signal' not in data.columns:
            return 0.0

        buy_signals = data[data['Signal'] == 1].index
        sell_signals = data[data['Signal'] == -1].index

        profits = []
        losses = []

        for buy_idx in buy_signals:
            sell_after = sell_signals[sell_signals > buy_idx]
            if len(sell_after) > 0:
                sell_idx = sell_after[0]
                buy_price = data.loc[buy_idx, 'Close']
                sell_price = data.loc[sell_idx, 'Close']

                pnl = sell_price / buy_price - 1

                if pnl > 0:
                    profits.append(pnl)
                else:
                    losses.append(abs(pnl))

        if not losses or not profits:
            return 0.0

        avg_profit = np.mean(profits) if profits else 0
        avg_loss = np.mean(losses) if losses else 0.001  # 0 제외

        return avg_profit / avg_loss if avg_loss > 0 else np.inf

    @staticmethod
    def calculate_total_trades(data: pd.DataFrame) -> int:
        """총 거래 수 계산"""
        if 'Signal' not in data.columns:
            return 0

        buy_signals = len(data[data['Signal'] == 1])
        sell_signals = len(data[data['Signal'] == -1])

        return min(buy_signals, sell_signals)

    @staticmethod
    def calculate_winning_trades(data: pd.DataFrame) -> int:
        """수익 거래 수 계산"""
        if 'Signal' not in data.columns:
            return 0

        buy_signals = data[data['Signal'] == 1].index
        sell_signals = data[data['Signal'] == -1].index

        winning = 0

        for buy_idx in buy_signals:
            sell_after = sell_signals[sell_signals > buy_idx]
            if len(sell_after) > 0:
                sell_idx = sell_after[0]
                if data.loc[sell_idx, 'Close'] > data.loc[buy_idx, 'Close']:
                    winning += 1

        return winning

    @staticmethod
    def calculate_losing_trades(data: pd.DataFrame) -> int:
        """손실 거래 수 계산"""
        total = MetricsCalculator.calculate_total_trades(data)
        winning = MetricsCalculator.calculate_winning_trades(data)
        return total - winning

    @staticmethod
    def calculate_avg_holding_period(data: pd.DataFrame) -> float:
        """평균 보유 기간 계산 (영업일 기준)"""
        if 'Signal' not in data.columns:
            return 0.0

        buy_signals = data[data['Signal'] == 1].index
        sell_signals = data[data['Signal'] == -1].index

        periods = []

        for buy_idx in buy_signals:
            sell_after = sell_signals[sell_signals > buy_idx]
            if len(sell_after) > 0:
                sell_idx = sell_after[0]
                period = len(data.loc[buy_idx:sell_idx])
                periods.append(period)

        if not periods:
            return 0.0

        return np.mean(periods)

    @staticmethod
    def calculate_calmar_ratio(cagr: float, max_drawdown: float) -> float:
        """칼마 비율 계산"""
        if max_drawdown == 0 or max_drawdown > -0.001:
            return 0.0

        return cagr / abs(max_drawdown)
