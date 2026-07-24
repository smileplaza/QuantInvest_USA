"""
yfinance wrapper for stock data download with error handling and caching
"""

import pandas as pd
import yfinance as yf
from datetime import datetime
import logging
from typing import Optional, Tuple

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class DataDownloadSignals(QObject):
    """신호를 정의하는 클래스"""
    progress = Signal(str)
    success = Signal(object)  # pandas DataFrame 전달 (Qt 타입이 아니므로 object 사용)
    error = Signal(str)


class DataDownloader:
    """Yahoo Finance에서 주식 데이터를 다운로드하는 클래스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def download_data(self, ticker: str, start_date, end_date) -> pd.DataFrame:
        """
        Yahoo Finance에서 주식 데이터 다운로드

        Args:
            ticker (str): 주식 티커 기호 (예: AAPL)
            start_date: 시작 날짜 (QDate 또는 string 'YYYY-MM-DD')
            end_date: 종료 날짜 (QDate 또는 string 'YYYY-MM-DD')

        Returns:
            pd.DataFrame: OHLCV 데이터를 포함한 데이터프레임

        Raises:
            ValueError: 유효하지 않은 입력
            ConnectionError: 데이터 다운로드 실패
        """

        # QDate를 문자열로 변환
        if hasattr(start_date, 'toString'):
            start_str = start_date.toString('yyyy-MM-dd')
        else:
            start_str = str(start_date)

        if hasattr(end_date, 'toString'):
            end_str = end_date.toString('yyyy-MM-dd')
        else:
            end_str = str(end_date)

        try:
            self.logger.info(f"Yahoo Finance에서 {ticker} 데이터 다운로드: {start_str} ~ {end_str}")

            # yfinance.download() with updated parameters
            data = yf.download(
                ticker,
                start=start_str,
                end=end_str,
                multi_level_index=False,
                auto_adjust=False,
                progress=False  # 진행률 표시 비활성화
            )

            if data.empty:
                raise ValueError(f"'{ticker}'에 대한 데이터를 찾을 수 없습니다. 티커를 확인해주세요.")

            # 데이터 검증
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                if col not in data.columns:
                    raise ValueError(f"필수 열이 없습니다: {col}")

            self.logger.info(f"성공: {len(data)} 행의 데이터 다운로드됨")
            return data

        except Exception as e:
            error_msg = self._parse_error(str(e), ticker)
            self.logger.error(f"다운로드 실패: {error_msg}")
            raise ConnectionError(error_msg)

    @staticmethod
    def _parse_error(error_str: str, ticker: str) -> str:
        """에러 메시지를 사용자 친화적으로 변환"""
        error_str_lower = error_str.lower()

        if 'no data found' in error_str_lower or 'invalid' in error_str_lower:
            return f"'{ticker}'의 데이터를 찾을 수 없습니다. 티커를 확인해주세요."
        elif 'connection' in error_str_lower or 'timeout' in error_str_lower:
            return "인터넷 연결을 확인해주세요. Yahoo Finance에 연결할 수 없습니다."
        elif 'date' in error_str_lower:
            return "날짜 범위가 유효하지 않습니다. 시작 날짜가 종료 날짜보다 앞인지 확인해주세요."
        else:
            return f"데이터 다운로드 실패: {error_str}"


class DataDownloadWorker(QObject):
    """백그라운드에서 데이터를 다운로드하는 워커 (QThread로 moveToThread 하여 사용)"""

    finished = Signal()

    def __init__(self, downloader: DataDownloader, ticker: str, start_date: str, end_date: str, signals: DataDownloadSignals):
        super().__init__()
        self.downloader = downloader
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.signals = signals

    def run(self):
        """워커 스레드 실행"""
        try:
            self.signals.progress.emit("데이터 다운로드 중...")

            data = self.downloader.download_data(self.ticker, self.start_date, self.end_date)

            self.signals.progress.emit(f"{len(data)} 행 다운로드 완료")
            self.signals.success.emit(data)
            self.finished.emit()

        except Exception as e:
            self.signals.error.emit(str(e))
            self.finished.emit()
