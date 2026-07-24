"""
데이터 형식 지정 유틸리티
"""

from PySide6.QtCore import QDate
from datetime import datetime


class NumberFormatter:
    """숫자 형식 지정 클래스"""

    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """
        백분율로 형식화

        Args:
            value (float): 값 (0.38은 38%)
            decimals (int): 소수 자릿수

        Returns:
            str: 형식화된 문자열 (예: "38.00%")
        """
        return f"{value * 100:.{decimals}f}%"

    @staticmethod
    def format_currency(value: float, decimals: int = 2) -> str:
        """
        통화로 형식화

        Args:
            value (float): 값
            decimals (int): 소수 자릿수

        Returns:
            str: 형식화된 문자열 (예: "$1,234.56")
        """
        return f"${value:,.{decimals}f}"

    @staticmethod
    def format_number(value: float, decimals: int = 2) -> str:
        """
        천 단위 쉼표를 포함하여 숫자로 형식화

        Args:
            value (float): 값
            decimals (int): 소수 자릿수

        Returns:
            str: 형식화된 문자열 (예: "1,234.56")
        """
        return f"{value:,.{decimals}f}"

    @staticmethod
    def format_integer(value: int) -> str:
        """
        천 단위 쉼표를 포함하여 정수로 형식화

        Args:
            value (int): 값

        Returns:
            str: 형식화된 문자열 (예: "1,234")
        """
        return f"{value:,}"

    @staticmethod
    def format_days(days: int) -> str:
        """
        일수를 문자열로 형식화

        Args:
            days (int): 일수

        Returns:
            str: 형식화된 문자열 (예: "10일")
        """
        return f"{days}일"

    @staticmethod
    def format_ratio(value: float, decimals: int = 2) -> str:
        """
        비율로 형식화

        Args:
            value (float): 비율 값
            decimals (int): 소수 자릿수

        Returns:
            str: 형식화된 문자열 (예: "4.92")
        """
        return f"{value:.{decimals}f}"


class DateFormatter:
    """날짜 형식 지정 클래스"""

    @staticmethod
    def format_qdate(qdate: QDate, format_str: str = "yyyy-MM-dd") -> str:
        """
        QDate를 문자열로 형식화

        Args:
            qdate (QDate): QDate 객체
            format_str (str): 형식 문자열

        Returns:
            str: 형식화된 날짜 문자열
        """
        return qdate.toString(format_str)

    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d") -> str:
        """
        datetime을 문자열로 형식화

        Args:
            dt (datetime): datetime 객체
            format_str (str): 형식 문자열

        Returns:
            str: 형식화된 날짜 문자열
        """
        return dt.strftime(format_str)

    @staticmethod
    def format_date_range(start: QDate, end: QDate) -> str:
        """
        날짜 범위를 문자열로 형식화

        Args:
            start (QDate): 시작 날짜
            end (QDate): 종료 날짜

        Returns:
            str: 형식화된 문자열 (예: "2023-01-01 ~ 2024-01-01")
        """
        start_str = start.toString("yyyy-MM-dd")
        end_str = end.toString("yyyy-MM-dd")
        return f"{start_str} ~ {end_str}"


class MetricFormatter:
    """성능 지표 형식 지정 클래스"""

    @staticmethod
    def format_cagr(value: float) -> str:
        """CAGR 형식화"""
        return NumberFormatter.format_percentage(value, 2)

    @staticmethod
    def format_sharpe_ratio(value: float) -> str:
        """샤프 지수 형식화"""
        return NumberFormatter.format_ratio(value, 2)

    @staticmethod
    def format_max_drawdown(value: float) -> str:
        """최대 낙폭 형식화"""
        return NumberFormatter.format_percentage(value, 2)

    @staticmethod
    def format_win_rate(value: float) -> str:
        """승률 형식화"""
        return NumberFormatter.format_percentage(value, 2)

    @staticmethod
    def format_profit_loss_ratio(value: float) -> str:
        """수익/손실 비율 형식화"""
        return NumberFormatter.format_ratio(value, 2)

    @staticmethod
    def format_trade_count(count: int) -> str:
        """거래 수 형식화"""
        return NumberFormatter.format_integer(count)

    @staticmethod
    def format_holding_period(days: float) -> str:
        """보유 기간 형식화"""
        return f"{days:.1f}일"

    @staticmethod
    def format_metrics_table(metrics: dict) -> dict:
        """
        모든 지표를 형식화된 딕셔너리로 변환

        Args:
            metrics (dict): 원본 지표 딕셔너리

        Returns:
            dict: 형식화된 지표 딕셔너리
        """
        formatted = {}

        if 'cagr' in metrics:
            formatted['CAGR'] = MetricFormatter.format_cagr(metrics['cagr'])
        if 'sharpe_ratio' in metrics:
            formatted['Sharpe Ratio'] = MetricFormatter.format_sharpe_ratio(metrics['sharpe_ratio'])
        if 'max_drawdown' in metrics:
            formatted['Max Drawdown'] = MetricFormatter.format_max_drawdown(metrics['max_drawdown'])
        if 'win_rate' in metrics:
            formatted['Win Rate'] = MetricFormatter.format_win_rate(metrics['win_rate'])
        if 'profit_loss_ratio' in metrics:
            formatted['P/L Ratio'] = MetricFormatter.format_profit_loss_ratio(metrics['profit_loss_ratio'])
        if 'total_trades' in metrics:
            formatted['Total Trades'] = MetricFormatter.format_trade_count(metrics['total_trades'])
        if 'winning_trades' in metrics:
            formatted['Winning Trades'] = MetricFormatter.format_trade_count(metrics['winning_trades'])
        if 'losing_trades' in metrics:
            formatted['Losing Trades'] = MetricFormatter.format_trade_count(metrics['losing_trades'])
        if 'avg_holding_period' in metrics:
            formatted['Avg Holding Period'] = MetricFormatter.format_holding_period(metrics['avg_holding_period'])

        return formatted
