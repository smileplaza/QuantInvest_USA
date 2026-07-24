"""
파라미터 최적화 모듈 - 병렬 처리 지원
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Callable, Optional
from multiprocessing import Pool, cpu_count
import logging

logger = logging.getLogger(__name__)


class ParameterOptimizer:
    """파라미터 최적화 수행 클래스"""

    def __init__(self, use_parallel: bool = False, n_jobs: Optional[int] = None):
        """
        최적화기 초기화

        Args:
            use_parallel (bool): 병렬 처리 사용 여부
            n_jobs (int): 병렬 작업 개수 (None시 자동 결정)
        """
        self.use_parallel = use_parallel
        self.n_jobs = n_jobs or max(1, cpu_count() - 1)
        self.logger = logging.getLogger(__name__)

    def optimize(
        self,
        strategy,
        data: pd.DataFrame,
        param_ranges: Dict
    ) -> Tuple[Dict, float, List[Dict]]:
        """
        전략 최적화 실행

        Args:
            strategy: BaseStrategy 인스턴스
            data (pd.DataFrame): OHLCV 데이터
            param_ranges (Dict): 파라미터 범위 {'param_name': (min, max, step), ...}

        Returns:
            Tuple: (최적 파라미터, 최대 수익률, 모든 결과)
        """
        if self.use_parallel:
            return self._optimize_parallel(strategy, data, param_ranges)
        else:
            return self._optimize_sequential(strategy, data, param_ranges)

    def _optimize_sequential(
        self,
        strategy,
        data: pd.DataFrame,
        param_ranges: Dict
    ) -> Tuple[Dict, float, List[Dict]]:
        """순차적 최적화"""
        best_params, best_return = strategy.optimize_parameters(data, param_ranges)

        combinations = strategy._generate_combinations(param_ranges)
        results = []

        for params in combinations:
            strategy.params = params.copy()
            try:
                signal_data = strategy.calculate_signals(data.copy())
                backtest_data = strategy.run_backtest(signal_data)
                final_return = backtest_data['Cumulative_Return'].iloc[-1] - 1
                results.append({**params, 'return': final_return})
            except Exception as e:
                self.logger.warning(f"조합 실패 - {params}: {e}")
                continue

        results_sorted = sorted(results, key=lambda x: x['return'], reverse=True)

        return best_params, best_return, results_sorted

    def _optimize_parallel(
        self,
        strategy,
        data: pd.DataFrame,
        param_ranges: Dict
    ) -> Tuple[Dict, float, List[Dict]]:
        """병렬 최적화"""
        self.logger.info(f"병렬 최적화 시작 ({self.n_jobs}개 프로세스)")

        combinations = strategy._generate_combinations(param_ranges)
        total = len(combinations)

        self.logger.info(f"총 {total}개 조합 평가")

        try:
            with Pool(self.n_jobs) as pool:
                results = []
                for i, result in enumerate(
                    pool.imap_unordered(
                        self._evaluate_combination,
                        [(strategy.__class__.__name__, params, data) for params in combinations]
                    )
                ):
                    if result is not None:
                        results.append(result)

                    if (i + 1) % max(1, total // 10) == 0:
                        self.logger.info(f"진행: {i + 1}/{total}")

        except Exception as e:
            self.logger.error(f"병렬 처리 오류: {e}")
            return self._optimize_sequential(strategy, data, param_ranges)

        if not results:
            return {}, 0.0, []

        best_result = max(results, key=lambda x: x['return'])
        best_params = {k: v for k, v in best_result.items() if k != 'return'}
        best_return = best_result['return']

        results_sorted = sorted(results, key=lambda x: x['return'], reverse=True)

        self.logger.info(f"병렬 최적화 완료 - 최선: {best_return:.2%}")

        return best_params, best_return, results_sorted

    @staticmethod
    def _evaluate_combination(args) -> Optional[Dict]:
        """조합 평가 (병렬 처리용 정적 메서드)"""
        strategy_name, params, data = args

        try:
            # 동적 import로 전략 클래스 생성
            from strategies.momentum_strategy import MomentumStrategy
            from strategies.trend_following import TrendFollowingStrategy
            from strategies.mean_reversion import MeanReversionStrategy
            from strategies.portfolio import PortfolioStrategy

            strategy_map = {
                'MomentumStrategy': MomentumStrategy,
                'TrendFollowingStrategy': TrendFollowingStrategy,
                'MeanReversionStrategy': MeanReversionStrategy,
                'PortfolioStrategy': PortfolioStrategy
            }

            strategy_class = strategy_map.get(strategy_name)
            if not strategy_class:
                return None

            strategy = strategy_class()
            strategy.params = params.copy()

            signal_data = strategy.calculate_signals(data.copy())
            backtest_data = strategy.run_backtest(signal_data)
            final_return = backtest_data['Cumulative_Return'].iloc[-1] - 1

            return {**params, 'return': final_return}

        except Exception as e:
            logger.warning(f"조합 평가 실패 - {params}: {e}")
            return None

    def get_top_results(
        self,
        results: List[Dict],
        n: int = 10
    ) -> List[Dict]:
        """상위 결과 반환"""
        sorted_results = sorted(results, key=lambda x: x['return'], reverse=True)
        return sorted_results[:n]

    def analyze_sensitivity(
        self,
        results: List[Dict],
        param_name: str
    ) -> Dict[float, float]:
        """특정 파라미터의 민감도 분석"""
        sensitivity = {}

        for result in results:
            param_value = result.get(param_name)
            return_value = result['return']

            if param_value not in sensitivity:
                sensitivity[param_value] = []

            sensitivity[param_value].append(return_value)

        # 각 파라미터 값의 평균 수익률 계산
        avg_sensitivity = {
            k: np.mean(v) for k, v in sensitivity.items()
        }

        return dict(sorted(avg_sensitivity.items(), key=lambda x: x[1], reverse=True))

    def export_results(
        self,
        results: List[Dict],
        output_path: str
    ) -> None:
        """결과를 CSV로 내보내기"""
        df = pd.DataFrame(results)
        df = df.sort_values('return', ascending=False)
        df.to_csv(output_path, index=False, encoding='utf-8')
        self.logger.info(f"결과 내보내기 완료: {output_path}")
