"""
SQLite-based caching system for stock data
"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """SQLite를 사용한 주식 데이터 캐싱 관리"""

    def __init__(self, db_path: str = "quantinvest_cache.db"):
        """
        캐시 매니저 초기화

        Args:
            db_path (str): SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()

    def _init_database(self):
        """데이터베이스 및 테이블 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 가격 히스토리 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    date DATE NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL NOT NULL,
                    volume INTEGER,
                    UNIQUE(ticker, date)
                )
            ''')

            # 티커별 인덱스 생성
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_ticker_date
                ON price_history(ticker, date)
            ''')

            conn.commit()
            conn.close()

            self.logger.info(f"데이터베이스 초기화 완료: {self.db_path}")

        except sqlite3.Error as e:
            self.logger.error(f"데이터베이스 초기화 실패: {e}")
            raise

    def get_data(self, ticker: str, start_date, end_date) -> Optional[pd.DataFrame]:
        """
        캐시에서 주식 데이터 검색

        Args:
            ticker (str): 주식 티커
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            pd.DataFrame 또는 None: 캐시된 데이터 또는 None
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
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()

            # 날짜 범위 내의 데이터 검색
            cursor.execute('''
                SELECT date, open, high, low, close, volume
                FROM price_history
                WHERE ticker = ? AND date BETWEEN ? AND ?
                ORDER BY date
            ''', (ticker.upper(), start_str, end_str))

            rows = cursor.fetchall()
            conn.close()

            if not rows:
                self.logger.debug(f"캐시에서 데이터 없음: {ticker} ({start_str} ~ {end_str})")
                return None

            # DataFrame으로 변환 (sqlite3.Row → dict로 컬럼명 보존)
            df = pd.DataFrame([dict(row) for row in rows])
            df['Date'] = pd.to_datetime(df['date'])
            df = df.set_index('Date')
            df = df.drop('date', axis=1)

            # 열 이름 표준화
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

            self.logger.info(f"캐시에서 로드됨: {ticker} ({len(df)}행)")
            return df

        except sqlite3.Error as e:
            self.logger.error(f"캐시 읽기 실패: {e}")
            return None

    def store_data(self, ticker: str, data: pd.DataFrame):
        """
        주식 데이터를 캐시에 저장

        Args:
            ticker (str): 주식 티커
            data (pd.DataFrame): 저장할 데이터
        """

        if data is None or data.empty:
            self.logger.warning(f"데이터가 비어있음: {ticker}")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            ticker = ticker.upper()

            # 데이터 삽입 (기존 데이터는 업데이트)
            for idx, row in data.iterrows():
                date_str = idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx)

                cursor.execute('''
                    INSERT OR REPLACE INTO price_history
                    (ticker, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ticker,
                    date_str,
                    float(row['Open']) if 'Open' in row else None,
                    float(row['High']) if 'High' in row else None,
                    float(row['Low']) if 'Low' in row else None,
                    float(row['Close']),
                    int(row['Volume']) if 'Volume' in row else None
                ))

            conn.commit()
            conn.close()

            self.logger.info(f"캐시에 저장됨: {ticker} ({len(data)}행)")

        except sqlite3.Error as e:
            self.logger.error(f"캐시 저장 실패: {e}")
            raise

    def clear_all(self):
        """모든 캐시 데이터 삭제"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM price_history')
            conn.commit()
            conn.close()

            self.logger.info("모든 캐시 데이터 삭제됨")

        except sqlite3.Error as e:
            self.logger.error(f"캐시 삭제 실패: {e}")
            raise

    def clear_ticker(self, ticker: str):
        """특정 티커의 캐시 데이터 삭제"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM price_history WHERE ticker = ?', (ticker.upper(),))
            conn.commit()
            conn.close()

            self.logger.info(f"캐시 삭제됨: {ticker}")

        except sqlite3.Error as e:
            self.logger.error(f"캐시 삭제 실패: {e}")
            raise

    def get_cached_tickers(self) -> list:
        """캐시에 저장된 모든 티커 목록 반환"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT ticker FROM price_history ORDER BY ticker')
            tickers = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tickers

        except sqlite3.Error as e:
            self.logger.error(f"티커 목록 조회 실패: {e}")
            return []

    def get_cache_info(self) -> dict:
        """캐시 정보 반환"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 총 레코드 수
            cursor.execute('SELECT COUNT(*) FROM price_history')
            total_records = cursor.fetchone()[0]

            # 티커 수
            cursor.execute('SELECT COUNT(DISTINCT ticker) FROM price_history')
            unique_tickers = cursor.fetchone()[0]

            # 날짜 범위
            cursor.execute('SELECT MIN(date), MAX(date) FROM price_history')
            date_range = cursor.fetchone()

            conn.close()

            return {
                'total_records': total_records,
                'unique_tickers': unique_tickers,
                'earliest_date': date_range[0],
                'latest_date': date_range[1],
                'db_size': Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
            }

        except sqlite3.Error as e:
            self.logger.error(f"캐시 정보 조회 실패: {e}")
            return {}
