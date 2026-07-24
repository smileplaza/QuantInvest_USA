"""
평균 회귀 거래 전략 구현
Z-점수 기반 통계적 반전 거래
"""

import pandas as pd
import numpy as np
from scipy import stats
from .base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """Z-점수 기반 평균 회귀 전략"""

    def __init__(self, initial_capital: float = 10000, transaction_fee: float = 0.001):
        super().__init__(initial_capital, transaction_fee)
        self.params = {
            'lookback_period': 20,
            'z_score_threshold': 1.96,
            'position_size': 0.5
        }

    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """기술 지표 계산 및 신호 생성"""
        data = data.copy()

        lookback_period = self.params.get('lookback_period', 20)
        z_threshold = self.params.get('z_score_threshold', 1.96)

        # 수익률 계산
        data['Returns'] = data['Close'].pct_change()

        # 이동 평균과 표준편차
        data['MA'] = data['Close'].rolling(lookback_period).mean()
        data['Std'] = data['Close'].rolling(lookback_period).std()

        # Z-점수
        data['Z_Score'] = (data['Close'] - data['MA']) / data['Std']
        data = data.dropna()

        # 신호 생성
        data['Position'] = 0
        data.loc[data['Z_Score'] < -z_threshold, 'Position'] = 1  # 매도
        data.loc[data['Z_Score'] > z_threshold, 'Position'] = -1  # 매수

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
