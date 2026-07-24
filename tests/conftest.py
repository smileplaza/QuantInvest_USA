"""
pytest 공통 픽스처 정의
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# src 디렉터리를 import 경로에 추가
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _make_ohlcv(n: int, seed: int, trend: float = 0.0) -> pd.DataFrame:
    """재현 가능한 합성 OHLCV 데이터 생성"""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-01", periods=n, freq="B")
    steps = rng.normal(trend, 1.0, n)
    close = 100 + np.cumsum(steps)
    close = np.maximum(close, 1.0)  # 음수 가격 방지
    return pd.DataFrame(
        {
            "Open": close * 0.99,
            "High": close * 1.02,
            "Low": close * 0.98,
            "Close": close,
            "Volume": rng.integers(1_000_000, 5_000_000, n),
        },
        index=idx,
    )


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """기본 합성 데이터 (300 영업일, 상승 편향)"""
    return _make_ohlcv(n=300, seed=42, trend=0.05)


@pytest.fixture
def flat_data() -> pd.DataFrame:
    """추세 없는 횡보 데이터"""
    return _make_ohlcv(n=250, seed=7, trend=0.0)


@pytest.fixture
def short_data() -> pd.DataFrame:
    """짧은 기간 데이터 (엣지 케이스)"""
    return _make_ohlcv(n=60, seed=13, trend=0.02)


@pytest.fixture
def make_ohlcv():
    """커스텀 파라미터로 데이터를 생성하는 팩토리"""
    return _make_ohlcv
