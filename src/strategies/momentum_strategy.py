"""
모멘텀 거래 전략 구현
가격 모멘텀 + Money Flow Index (MFI) 거래량 확인
"""

import pandas as pd
import numpy as np
from typing import Dict
import ta
from .base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """모멘텀 거래 전략"""

    def __init__(self, initial_capital: float = 10000, transaction_fee: float = 0.001):
        super().__init__(initial_capital, transaction_fee)
        self.params = {
            'momentum_period': 12,
            'mfi_level': 46.5,
            'stop_loss': 0.07
        }

    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        기술 지표 계산 및 매수/매도 신호 생성

        Args:
            data (pd.DataFrame): OHLCV 데이터

        Returns:
            pd.DataFrame: 신호가 포함된 데이터프레임
        """
        data = data.copy()

        # 파라미터
        momentum_period = self.params.get('momentum_period', 12)
        mfi_period = self.params.get('mfi_period', 7)
        mfi_threshold = self.params.get('mfi_level', 46.5)

        # 모멘텀 지표 계산
        data['Momentum'] = data['Close'].pct_change(periods=momentum_period)

        # MFI (Money Flow Index) 계산
        if 'High' in data.columns and 'Low' in data.columns and 'Volume' in data.columns:
            data['MFI'] = ta.volume.money_flow_index(
                data['High'],
                data['Low'],
                data['Close'],
                data['Volume'],
                window=mfi_period
            )
        else:
            # MFI 데이터 없으면 MFI 체크 스킵
            data['MFI'] = 50  # 중립값

        data = data.dropna()

        # 매도 신호 생성 (모멘텀 양수)
        momentum_signal = np.where(data['Momentum'] > 0, 1, 0)

        # MFI 필터 (MFI > threshold일 때만 매수)
        mfi_filter = np.where(data['MFI'] > mfi_threshold, 1, 0)

        # 결합 신호
        combined_signal = momentum_signal * mfi_filter

        # 신호 변화 감지 (1: 매수, -1: 매도, 0: 중립)
        data['Position'] = combined_signal
        data['Signal'] = data['Position'].diff().fillna(0)

        return data

    def run_backtest(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        백테스트 실행 (이벤트 기반)

        Args:
            data (pd.DataFrame): 신호가 포함된 데이터프레임

        Returns:
            pd.DataFrame: 백테스트 결과
        """
        data = data.copy()
        self._validate_backtest_data(data)

        # 파라미터
        stop_loss_pct = self.params.get('stop_loss', 0.07)

        # 초기화
        cash = self.initial_capital
        position = 0  # 0: 보유 없음, 1: 보유 중
        shares = 0
        entry_price = 0
        stop_loss_price = 0

        # 추적 배열
        portfolio_values = np.zeros(len(data))
        portfolio_values[0] = cash

        prices = data['Close'].values
        signals = data['Signal'].values

        # 백테스트 루프
        for i in range(1, len(data)):
            current_price = prices[i]

            if position == 0:  # 포지션 없음
                if signals[i] == 1:  # 매수 신호
                    shares, cash = self._execute_buy(current_price, cash, self.transaction_fee)
                    position = 1
                    entry_price = current_price
                    stop_loss_price = entry_price * (1 - stop_loss_pct)

            elif position == 1:  # 포지션 보유 중
                # 손절 확인
                if current_price < stop_loss_price:
                    cash += self._execute_sell(current_price, shares, self.transaction_fee)
                    position = 0
                    shares = 0
                else:
                    # 손절가 갱신 (상승에만)
                    new_stop_loss = current_price * (1 - stop_loss_pct)
                    stop_loss_price = max(stop_loss_price, new_stop_loss)

                    # 매도 신호 확인
                    if signals[i] == -1:
                        cash += self._execute_sell(current_price, shares, self.transaction_fee)
                        position = 0
                        shares = 0

            # 포트폴리오 가치 업데이트
            if position == 0:
                portfolio_values[i] = cash
            else:
                portfolio_values[i] = cash + current_price * shares

        # 결과 저장
        data['Portfolio_Value'] = portfolio_values
        data['Cumulative_Return'] = portfolio_values / self.initial_capital

        return data

    def __repr__(self) -> str:
        return (
            f"MomentumStrategy("
            f"momentum_period={self.params['momentum_period']}, "
            f"mfi_level={self.params['mfi_level']}, "
            f"stop_loss={self.params['stop_loss']})"
        )
