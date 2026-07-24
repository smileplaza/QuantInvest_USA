"""
추세 추종 거래 전략 구현
지수이동평균(EMA) 크로스오버 기반
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class TrendFollowingStrategy(BaseStrategy):
    """EMA 크로스오버 추세 추종 전략"""

    def __init__(self, initial_capital: float = 10000, transaction_fee: float = 0.001):
        super().__init__(initial_capital, transaction_fee)
        self.params = {
            'short_window': 12,
            'long_window': 26,
            'stop_loss': 0.07
        }

    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술 지표 계산 및 신호 생성"""
        data = data.copy()

        short_window = self.params.get('short_window', 12)
        long_window = self.params.get('long_window', 26)

        # EMA 계산 (adjust=False: 표준 재귀식 EMA, 원본 노트북 ch_06/07과 일치)
        data['Short_EMA'] = data['Close'].ewm(span=short_window, adjust=False).mean()
        data['Long_EMA'] = data['Close'].ewm(span=long_window, adjust=False).mean()

        # 신호 생성 (골든/데드 크로스)
        data['Position'] = np.where(data['Short_EMA'] > data['Long_EMA'], 1, 0)
        data['Signal'] = data['Position'].diff().fillna(0)

        return data

    def run_backtest(self, data: pd.DataFrame) -> pd.DataFrame:
        """백테스트 실행"""
        data = data.copy()
        self._validate_backtest_data(data)
        stop_loss_pct = self.params.get('stop_loss', 0.07)

        cash = self.initial_capital
        position = 0
        shares = 0
        entry_price = 0
        stop_loss_price = 0

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
                    entry_price = current_price
                    stop_loss_price = entry_price * (1 - stop_loss_pct)

            elif position == 1:
                if current_price < stop_loss_price:
                    cash += self._execute_sell(current_price, shares, self.transaction_fee)
                    position = 0
                else:
                    stop_loss_price = max(stop_loss_price, current_price * (1 - stop_loss_pct))
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
