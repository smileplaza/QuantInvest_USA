"""
백테스팅 엔진 - 거래 전략 시뮬레이션
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class BacktestEngine:
    """거래 전략 백테스트 실행 엔진"""

    def __init__(self, initial_capital: float = 10000, transaction_fee: float = 0.001,
                 risk_free_rate: float = 0.003):
        """
        엔진 초기화

        Args:
            initial_capital (float): 초기 자본
            transaction_fee (float): 거래 수수료율
            risk_free_rate (float): 샤프 지수 계산용 무위험 이율
        """
        self.initial_capital = initial_capital
        self.transaction_fee = transaction_fee
        self.risk_free_rate = risk_free_rate
        self.logger = logging.getLogger(__name__)

    def run_strategy(self, strategy, data: pd.DataFrame) -> Dict:
        """
        전략 실행 및 결과 반환

        Args:
            strategy: BaseStrategy 인스턴스
            data (pd.DataFrame): OHLCV 데이터

        Returns:
            Dict: 백테스트 결과
        """
        try:
            self.logger.info(f"백테스트 시작: {strategy.__class__.__name__}")

            # 신호 계산
            signal_data = strategy.calculate_signals(data.copy())

            # 백테스트 실행
            result_data = strategy.run_backtest(signal_data)

            # 메트릭 계산
            from .metrics import MetricsCalculator
            metrics_calc = MetricsCalculator(risk_free_rate=self.risk_free_rate)

            metrics = metrics_calc.calculate_all_metrics(result_data, self.initial_capital)

            self.logger.info(f"백테스트 완료: CAGR={metrics['cagr']:.2%}")

            return {
                'data': result_data,
                'metrics': metrics,
                'strategy': strategy
            }

        except Exception as e:
            self.logger.error(f"백테스트 오류: {e}")
            raise

    def run_optimization(self, strategy, data: pd.DataFrame, param_ranges: Dict) -> Dict:
        """
        파라미터 최적화 실행

        Args:
            strategy: BaseStrategy 인스턴스
            data (pd.DataFrame): OHLCV 데이터
            param_ranges (Dict): 파라미터 범위

        Returns:
            Dict: 최적화 결과
        """
        try:
            self.logger.info(f"최적화 시작: {strategy.__class__.__name__}")

            optimal_params, best_return = strategy.optimize_parameters(data.copy(), param_ranges)

            self.logger.info(f"최적화 완료: 최선 수익률={best_return:.2%}")

            return {
                'optimal_params': optimal_params,
                'best_return': best_return,
                'strategy': strategy
            }

        except Exception as e:
            self.logger.error(f"최적화 오류: {e}")
            raise

    def compare_strategies(self, strategies: List, data: pd.DataFrame) -> Dict:
        """
        여러 전략 비교

        Args:
            strategies (List): BaseStrategy 인스턴스 리스트
            data (pd.DataFrame): OHLCV 데이터

        Returns:
            Dict: 전략별 결과 비교
        """
        results = {}

        for strategy in strategies:
            try:
                result = self.run_strategy(strategy, data.copy())
                results[strategy.__class__.__name__] = result['metrics']
            except Exception as e:
                self.logger.error(f"{strategy.__class__.__name__} 실행 실패: {e}")
                continue

        return results

    def generate_report(self, result: Dict, output_path: str = None) -> str:
        """
        백테스트 결과 보고서 생성

        Args:
            result (Dict): 백테스트 결과
            output_path (str): 저장 경로 (선택사항)

        Returns:
            str: 보고서 내용
        """
        metrics = result['metrics']
        strategy = result['strategy']

        report = f"""
================================
백테스트 결과 보고서
================================

전략: {strategy.__class__.__name__}
파라미터: {strategy.params}

성능 지표:
----------
CAGR:                {metrics['cagr']:.2%}
샤프 지수:           {metrics['sharpe_ratio']:.2f}
최대 낙폭:           {metrics['max_drawdown']:.2%}
승률:               {metrics['win_rate']:.2%}
수익/손실 비율:      {metrics['profit_loss_ratio']:.2f}

거래 정보:
----------
총 거래:             {metrics['total_trades']}
수익 거래:           {metrics['winning_trades']}
손실 거래:           {metrics['losing_trades']}
평균 보유 기간:      {metrics['avg_holding_period']:.1f}일

================================
"""

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            self.logger.info(f"보고서 저장: {output_path}")

        return report
