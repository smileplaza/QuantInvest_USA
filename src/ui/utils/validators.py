"""
입력 검증 유틸리티
"""

from PySide6.QtCore import QDate
from typing import Tuple


class InputValidator:
    """입력값 검증 클래스"""

    @staticmethod
    def validate_ticker(ticker: str) -> Tuple[bool, str]:
        """
        주식 티커 검증

        Args:
            ticker (str): 검증할 티커

        Returns:
            Tuple[bool, str]: (유효 여부, 에러 메시지)
        """
        if not ticker:
            return False, "티커를 입력해주세요"

        ticker = ticker.strip()
        if not (1 <= len(ticker) <= 5):
            return False, "티커는 1-5자여야 합니다"

        if not ticker.isalnum():
            return False, "티커는 영문자와 숫자만 포함해야 합니다"

        return True, ""

    @staticmethod
    def validate_date_range(start: QDate, end: QDate) -> Tuple[bool, str]:
        """
        날짜 범위 검증

        Args:
            start (QDate): 시작 날짜
            end (QDate): 종료 날짜

        Returns:
            Tuple[bool, str]: (유효 여부, 에러 메시지)
        """
        if start > end:
            return False, "시작 날짜는 종료 날짜보다 빨라야 합니다"

        years_diff = end.year() - start.year()
        if years_diff > 30:
            return False, "날짜 범위는 30년을 초과할 수 없습니다"

        if start == end:
            return False, "시작 날짜와 종료 날짜가 같을 수 없습니다"

        return True, ""

    @staticmethod
    def validate_strategy_params(strategy: str, params: dict) -> Tuple[bool, str]:
        """
        전략 파라미터 검증

        Args:
            strategy (str): 전략 이름
            params (dict): 파라미터 딕셔너리

        Returns:
            Tuple[bool, str]: (유효 여부, 에러 메시지)
        """
        # 전략별 파라미터 정의
        STRATEGY_PARAMS = {
            "Momentum": {
                "momentum_period": {"type": "int", "min": 3, "max": 30},
                "mfi_level": {"type": "float", "min": 20, "max": 80},
                "stop_loss": {"type": "float", "min": 0.01, "max": 0.20}
            },
            "TrendFollowing": {
                "short_window": {"type": "int", "min": 5, "max": 30},
                "long_window": {"type": "int", "min": 20, "max": 100},
                "stop_loss": {"type": "float", "min": 0.01, "max": 0.20}
            },
            "MeanReversion": {
                "lookback_period": {"type": "int", "min": 5, "max": 50},
                "z_score": {"type": "float", "min": 0.5, "max": 3.0},
                "position_size": {"type": "float", "min": 0.01, "max": 1.0}
            },
            "Portfolio": {
                "portfolio_size": {"type": "int", "min": 2, "max": 10},
                "correlation_filter": {"type": "float", "min": 0.0, "max": 1.0},
                "weight_method": {"type": "str", "options": ["equal", "market_cap", "inverse_variance"]}
            }
        }

        if strategy not in STRATEGY_PARAMS:
            return False, f"알 수 없는 전략: {strategy}"

        spec = STRATEGY_PARAMS[strategy]

        for param_name, param_value in params.items():
            if param_name not in spec:
                return False, f"알 수 없는 파라미터: {param_name}"

            param_spec = spec[param_name]

            # 타입 검증
            if param_spec.get("type") == "int":
                if not isinstance(param_value, int):
                    return False, f"{param_name}는 정수여야 합니다"
            elif param_spec.get("type") == "float":
                if not isinstance(param_value, (int, float)):
                    return False, f"{param_name}는 숫자여야 합니다"
            elif param_spec.get("type") == "str":
                if not isinstance(param_value, str):
                    return False, f"{param_name}는 문자열이어야 합니다"

            # 범위 검증
            if "min" in param_spec and param_value < param_spec["min"]:
                return False, f"{param_name}는 {param_spec['min']} 이상이어야 합니다"

            if "max" in param_spec and param_value > param_spec["max"]:
                return False, f"{param_name}는 {param_spec['max']} 이하여야 합니다"

            # 선택지 검증
            if "options" in param_spec and param_value not in param_spec["options"]:
                return False, f"{param_name}의 값이 유효하지 않습니다"

        return True, ""

    @staticmethod
    def validate_optimization_ranges(param_ranges: dict) -> Tuple[bool, str]:
        """
        최적화 파라미터 범위 검증

        Args:
            param_ranges (dict): 파라미터 범위 딕셔너리

        Returns:
            Tuple[bool, str]: (유효 여부, 에러 메시지)
        """
        if not param_ranges:
            return False, "최소 1개 이상의 파라미터 범위가 필요합니다"

        for param_name, (min_val, max_val, step) in param_ranges.items():
            if min_val >= max_val:
                return False, f"{param_name}: 최소값이 최대값보다 작아야 합니다"

            if step <= 0:
                return False, f"{param_name}: 단계값은 0보다 커야 합니다"

        return True, ""
