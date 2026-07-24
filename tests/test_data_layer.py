"""
데이터 계층 (캐시) 단위 테스트
"""

import pandas as pd
import pytest

from data.cache import CacheManager


@pytest.fixture
def cache(tmp_path):
    """임시 SQLite 캐시 (테스트 격리)"""
    db_path = tmp_path / "test_cache.db"
    return CacheManager(db_path=str(db_path))


@pytest.fixture
def price_frame():
    idx = pd.date_range("2023-01-02", periods=5, freq="B")
    return pd.DataFrame(
        {
            "Open": [100, 101, 102, 103, 104],
            "High": [101, 102, 103, 104, 105],
            "Low": [99, 100, 101, 102, 103],
            "Close": [100.5, 101.5, 102.5, 103.5, 104.5],
            "Volume": [1_000_000, 1_100_000, 1_200_000, 1_300_000, 1_400_000],
        },
        index=idx,
    )


class TestCacheStoreAndRetrieve:
    """저장 및 조회 왕복 테스트"""

    def test_store_then_get(self, cache, price_frame):
        cache.store_data("AAPL", price_frame)
        result = cache.get_data("AAPL", "2023-01-02", "2023-01-10")
        assert result is not None
        assert len(result) == 5
        assert list(result.columns) == ["Open", "High", "Low", "Close", "Volume"]

    def test_get_missing_returns_none(self, cache):
        assert cache.get_data("MSFT", "2023-01-01", "2023-12-31") is None

    def test_ticker_case_insensitive(self, cache, price_frame):
        cache.store_data("aapl", price_frame)
        result = cache.get_data("AAPL", "2023-01-02", "2023-01-10")
        assert result is not None
        assert len(result) == 5

    def test_date_range_filter(self, cache, price_frame):
        cache.store_data("AAPL", price_frame)
        # 부분 범위만 조회
        result = cache.get_data("AAPL", "2023-01-02", "2023-01-04")
        assert result is not None
        assert len(result) == 3

    def test_upsert_no_duplicates(self, cache, price_frame):
        cache.store_data("AAPL", price_frame)
        cache.store_data("AAPL", price_frame)  # 재저장
        result = cache.get_data("AAPL", "2023-01-02", "2023-01-10")
        assert len(result) == 5  # 중복 없음


class TestCacheManagement:
    """캐시 관리 기능 테스트"""

    def test_clear_all(self, cache, price_frame):
        cache.store_data("AAPL", price_frame)
        cache.clear_all()
        assert cache.get_data("AAPL", "2023-01-02", "2023-01-10") is None

    def test_clear_ticker(self, cache, price_frame):
        cache.store_data("AAPL", price_frame)
        cache.store_data("MSFT", price_frame)
        cache.clear_ticker("AAPL")
        assert cache.get_data("AAPL", "2023-01-02", "2023-01-10") is None
        assert cache.get_data("MSFT", "2023-01-02", "2023-01-10") is not None

    def test_get_cached_tickers(self, cache, price_frame):
        cache.store_data("AAPL", price_frame)
        cache.store_data("MSFT", price_frame)
        tickers = cache.get_cached_tickers()
        assert "AAPL" in tickers
        assert "MSFT" in tickers

    def test_get_cache_info(self, cache, price_frame):
        cache.store_data("AAPL", price_frame)
        info = cache.get_cache_info()
        assert info["total_records"] == 5
        assert info["unique_tickers"] == 1

    def test_store_empty_frame_noop(self, cache):
        cache.store_data("AAPL", pd.DataFrame())
        assert cache.get_cached_tickers() == []
