"""
거래 전략을 위한 추상 기본 클래스
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class InsufficientDataError(ValueError):
    """백테스트 수행에 필요한 데이터가 부족할 때 발생하는 예외.

    극단적인 파라미터(예: lookback 기간이 데이터 길이보다 큰 경우), 거래량이
    모두 0이어서 지표 계산 후 유효 데이터가 남지 않는 경우 등에서 발생한다.
    UI 계층이 사용자에게 친화적인 메시지를 표시할 수 있도록 ValueError를 상속한다.
    """
    pass


class BaseStrategy(ABC):
    """모든 거래 전략의 추상 기본 클래스"""

    # 백테스트를 의미 있게 수행하기 위한 최소 데이터 행 수
    MIN_BACKTEST_ROWS = 2

    def __init__(self, initial_capital: float = 10000, transaction_fee: float = 0.001):
        """
        전략 초기화

        Args:
            initial_capital (float): 초기 자본 (기본값: $10,000)
            transaction_fee (float): 거래 수수료율 (기본값: 0.1%)
        """
        self.initial_capital = initial_capital
        self.transaction_fee = transaction_fee
        self.params = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        기술 지표를 계산하고 매수/매도 신호를 생성

        Args:
            data (pd.DataFrame): OHLCV 데이터 (Open, High, Low, Close, Volume)

        Returns:
            pd.DataFrame: 'Signal' 열이 추가된 데이터프레임 (-1: 매도, 0: 중립, 1: 매수)
        """
        pass

    @abstractmethod
    def run_backtest(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        백테스트 실행

        Args:
            data (pd.DataFrame): 신호가 포함된 데이터프레임

        Returns:
            pd.DataFrame: 백테스트 결과 (Cumulative_Return 열 포함)
        """
        pass

    def optimize_parameters(self, data: pd.DataFrame, param_ranges: Dict) -> Tuple[Dict, float]:
        """
        파라미터 그리드 검색을 통한 최적화

        Args:
            data (pd.DataFrame): OHLCV 데이터
            param_ranges (Dict): 파라미터 범위 {'param_name': (min, max, step), ...}

        Returns:
            Tuple[Dict, float]: (최적 파라미터, 최대 수익률)
        """
        best_params = None
        best_return = -np.inf
        results = []

        # 파라미터 조합 생성
        combinations = self._generate_combinations(param_ranges)
        total_combinations = len(combinations)

        self.logger.info(f"최적화 시작: {total_combinations}개 조합")

        for i, params in enumerate(combinations):
            try:
                # 파라미터 설정
                self.params = params.copy()

                # 신호 계산
                signal_data = self.calculate_signals(data.copy())

                # 백테스트 실행
                backtest_data = self.run_backtest(signal_data)

                # 최종 수익률 계산
                final_return = backtest_data['Cumulative_Return'].iloc[-1] - 1

                results.append({**params, 'return': final_return})

                # 최선 찾기
                if final_return > best_return:
                    best_return = final_return
                    best_params = params.copy()

                # 진행 상황 로깅
                if (i + 1) % max(1, total_combinations // 10) == 0:
                    self.logger.info(f"진행: {i + 1}/{total_combinations}, 현재 최선: {best_return:.2%}")

            except Exception as e:
                self.logger.warning(f"조합 실패 - {params}: {e}")
                continue

        # 모든 조합이 실패한 경우 (예: 모든 파라미터가 데이터 길이를 초과)
        if best_params is None:
            raise InsufficientDataError(
                f"유효한 파라미터 조합을 찾지 못했습니다 (총 {total_combinations}개 "
                f"조합 모두 실패). 파라미터 범위를 줄이거나 더 긴 날짜 범위를 "
                f"선택해주세요."
            )

        self.logger.info(f"최적화 완료 - 최선: {best_params}, 수익률: {best_return:.2%}")
        self.params = best_params.copy()

        return best_params, best_return

    @staticmethod
    def _generate_combinations(param_ranges: Dict) -> List[Dict]:
        """
        파라미터 범위에서 모든 조합 생성

        Args:
            param_ranges (Dict): {'param_name': (min, max, step), ...}

        Returns:
            List[Dict]: 파라미터 조합 리스트
        """
        import itertools

        param_names = list(param_ranges.keys())
        param_values = []

        for name in param_names:
            min_val, max_val, step = param_ranges[name]

            # 범위 내의 모든 값 생성
            if isinstance(min_val, int) and isinstance(step, int):
                values = list(range(min_val, max_val + 1, step))
            else:
                num_steps = int((max_val - min_val) / step) + 1
                values = [min_val + i * step for i in range(num_steps)]

            param_values.append(values)

        # 모든 조합 생성
        combinations = []
        for values_tuple in itertools.product(*param_values):
            combo = {name: val for name, val in zip(param_names, values_tuple)}
            combinations.append(combo)

        return combinations

    def _validate_backtest_data(self, data: pd.DataFrame) -> None:
        """백테스트 실행 전 데이터 유효성 검사.

        지표 계산 및 dropna 이후 데이터가 백테스트를 수행하기에 충분한지 확인한다.

        Args:
            data (pd.DataFrame): 신호가 포함된 데이터프레임

        Raises:
            InsufficientDataError: 데이터가 비어 있거나 최소 행 수보다 적을 때
        """
        n = len(data)
        if n < self.MIN_BACKTEST_ROWS:
            raise InsufficientDataError(
                f"백테스트를 수행하기에 데이터가 부족합니다 (유효 {n}행, 최소 "
                f"{self.MIN_BACKTEST_ROWS}행 필요). 파라미터(기간)를 줄이거나 "
                f"더 긴 날짜 범위를 선택해주세요."
            )

    def _execute_buy(self, price: float, cash: float, fee_rate: float) -> Tuple[int, float]:
        """
        매수 실행

        Args:
            price (float): 매수 가격
            cash (float): 사용 가능한 현금
            fee_rate (float): 수수료율

        Returns:
            Tuple[int, float]: (매수 주식 수, 남은 현금)
        """
        # 수수료 포함 매수
        shares = int(cash / (price * (1 + fee_rate)))
        cost = price * shares * (1 + fee_rate)
        remaining_cash = cash - cost
        return shares, remaining_cash

    def _execute_sell(self, price: float, shares: int, fee_rate: float) -> float:
        """
        매도 실행

        Args:
            price (float): 매도 가격
            shares (int): 보유 주식 수
            fee_rate (float): 수수료율

        Returns:
            float: 매도 수익금
        """
        proceeds = price * shares * (1 - fee_rate)
        return proceeds

    def calculate_annual_return(self, cumulative_return: float, years: float) -> float:
        """
        CAGR 계산

        Args:
            cumulative_return (float): 누적 수익률
            years (float): 투자 기간 (연도)

        Returns:
            float: 연평균 성장률
        """
        if years <= 0:
            return 0.0
        return (1 + cumulative_return) ** (1 / years) - 1

    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.003) -> float:
        """
        샤프 지수 계산

        Args:
            returns (pd.Series): 일일 수익률
            risk_free_rate (float): 무위험 이율 (기본값: 0.3% 연율)

        Returns:
            float: 샤프 지수
        """
        mean_return = returns.mean() * 252  # 연율화
        std_return = returns.std() * np.sqrt(252)

        if std_return == 0:
            return 0.0

        return (mean_return - risk_free_rate) / std_return

    def calculate_max_drawdown(self, cumulative_returns: pd.Series) -> float:
        """
        최대 낙폭 계산

        Args:
            cumulative_returns (pd.Series): 누적 수익률

        Returns:
            float: 최대 낙폭 (음수)
        """
        running_max = cumulative_returns.cummax()
        drawdown = cumulative_returns / running_max - 1
        return drawdown.min()

    def calculate_win_rate(self, trades: List[Dict]) -> float:
        """
        승률 계산

        Args:
            trades (List[Dict]): 거래 리스트 [{'entry': price, 'exit': price}, ...]

        Returns:
            float: 승률 (0-1)
        """
        if not trades:
            return 0.0

        profitable = sum(1 for t in trades if t['exit'] > t['entry'])
        return profitable / len(trades)

    def summary(self) -> Dict:
        """전략 요약 정보 반환"""
        return {
            'strategy_name': self.__class__.__name__,
            'initial_capital': self.initial_capital,
            'transaction_fee': self.transaction_fee,
            'parameters': self.params
        }
