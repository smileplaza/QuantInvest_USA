"""
포트폴리오 최적화 거래 전략 구현
다중 주식 모멘텀 기반 포트폴리오 구성
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class PortfolioStrategy(BaseStrategy):
    """포트폴리오 최적화 전략"""

    def __init__(self, initial_capital: float = 10000, transaction_fee: float = 0.001):
        super().__init__(initial_capital, transaction_fee)
        self.params = {
            'portfolio_size': 5,
            'correlation_filter': 0.7,
            'weight_method': 'equal'
        }

    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        포트폴리오 신호 계산
        주식: data의 열 (Close, Volume 등)
        """
        data = data.copy()

        portfolio_size = self.params.get('portfolio_size', 5)
        momentum_period = self.params.get('momentum_period', 12)

        # 모멘텀 계산 (Close 열 사용)
        if 'Close' in data.columns:
            data['Momentum'] = data['Close'].pct_change(periods=momentum_period)
            data['Position'] = np.where(data['Momentum'] > 0, 1, 0)
            data['Signal'] = data['Position'].diff().fillna(0)

        return data

    def run_backtest(self, data: pd.DataFrame) -> pd.DataFrame:
        """백테스트 실행"""
        data = data.copy()
        self._validate_backtest_data(data)

        cash = self.initial_capital
        position = 0
        shares = 0

        portfolio_values = np.zeros(len(data))
        portfolio_values[0] = cash

        prices = data['Close'].values
        signals = data['Signal'].values

        for i in range(1, len(data)):
            current_price = prices[i]

            if position == 0:
                if signals[i] == 1:
                    shares, cash = self._execute_buy(current_price, cash, self.transaction_fee)
                    position = 1

            elif position == 1:
                if signals[i] == -1:
                    cash += self._execute_sell(current_price, shares, self.transaction_fee)
                    position = 0

            if position == 0:
                portfolio_values[i] = cash
            else:
                portfolio_values[i] = cash + current_price * shares

        data['Portfolio_Value'] = portfolio_values
        data['Cumulative_Return'] = portfolio_values / self.initial_capital

        return data
