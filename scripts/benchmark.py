"""
성능 벤치마크 / 프로파일링 스크립트

백테스트 속도와 파라미터 최적화 속도를 합성 데이터로 측정하여
TO_DO.md의 성능 목표 대비 결과를 출력한다.

목표(참고):
- 백테스트: 1년 <1초, 5년 <2초, 10년 <5초
- 최적화: 100 조합 <2분, 1000 조합 <10분

사용법:
    python scripts/benchmark.py [--profile]

--profile 옵션 지정 시 cProfile로 최적화 핫스팟 상위 항목을 함께 출력한다.
"""

import argparse
import cProfile
import io
import pstats
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# src 경로 등록
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from backtest.engine import BacktestEngine          # noqa: E402
from backtest.optimizer import ParameterOptimizer   # noqa: E402
from strategies.trend_following import TrendFollowingStrategy  # noqa: E402


def make_ohlcv(n: int, seed: int = 42) -> pd.DataFrame:
    """재현 가능한 합성 OHLCV 데이터 생성."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2000-01-01", periods=n, freq="B")
    close = 100 + np.cumsum(rng.normal(0.02, 1.0, n))
    close = np.maximum(close, 1.0)
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


def _timeit(fn, repeats: int = 3) -> float:
    """fn을 repeats회 실행한 최소 소요 시간(초) 반환."""
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - t0)
    return best


def bench_backtest() -> list:
    """기간별 백테스트 속도 측정."""
    print("\n=== 백테스트 속도 ===")
    engine = BacktestEngine()
    cases = [("1년", 252, 1.0), ("5년", 1260, 2.0), ("10년", 2520, 5.0)]
    rows = []
    for label, n, target in cases:
        data = make_ohlcv(n)
        strat = TrendFollowingStrategy()
        elapsed = _timeit(lambda: engine.run_strategy(strat, data))
        ok = "✓" if elapsed < target else "✗"
        print(f"  {label:4s} ({n:>4d}행): {elapsed*1000:8.2f} ms  (목표 <{target}s) {ok}")
        rows.append((label, n, elapsed, target, elapsed < target))
    return rows


def bench_optimization() -> list:
    """조합 수별 그리드 서치 최적화 속도 측정."""
    print("\n=== 최적화 속도 (그리드 서치) ===")
    data = make_ohlcv(1260)  # 5년
    optimizer = ParameterOptimizer(use_parallel=False)
    rows = []

    # 약 100 조합: short 5..14(10) x long 20..29(10) = 100, stop 고정
    grid_100 = {
        "short_window": (5, 14, 1),
        "long_window": (20, 29, 1),
        "stop_loss": (0.07, 0.07, 1),
    }
    # 약 1000 조합: 10 x 10 x 10
    grid_1000 = {
        "short_window": (5, 14, 1),
        "long_window": (20, 29, 1),
        "stop_loss": (0.03, 0.12, 0.01),
    }

    for label, grid, target_s in [("~100 조합", grid_100, 120), ("~1000 조합", grid_1000, 600)]:
        strat = TrendFollowingStrategy()
        combos = len(strat._generate_combinations(grid))
        t0 = time.perf_counter()
        optimizer.optimize(strat, data, grid)
        elapsed = time.perf_counter() - t0
        ok = "✓" if elapsed < target_s else "✗"
        print(f"  {label:10s} (실측 {combos:>4d}개): {elapsed:7.3f} s  (목표 <{target_s}s) {ok}")
        rows.append((label, combos, elapsed, target_s, elapsed < target_s))
    return rows


def profile_optimization():
    """cProfile로 최적화 핫스팟 상위 15개 출력."""
    print("\n=== 프로파일링: 최적화 핫스팟 (상위 15) ===")
    data = make_ohlcv(1260)
    optimizer = ParameterOptimizer(use_parallel=False)
    strat = TrendFollowingStrategy()
    grid = {
        "short_window": (5, 14, 1),
        "long_window": (20, 29, 1),
        "stop_loss": (0.07, 0.07, 1),
    }

    profiler = cProfile.Profile()
    profiler.enable()
    optimizer.optimize(strat, data, grid)
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(15)
    print(stream.getvalue())


def main():
    parser = argparse.ArgumentParser(description="QuantInvest 성능 벤치마크")
    parser.add_argument("--profile", action="store_true", help="cProfile 핫스팟 출력")
    args = parser.parse_args()

    print("=" * 60)
    print("QuantInvest Tool - 성능 벤치마크")
    print("=" * 60)

    bt_rows = bench_backtest()
    opt_rows = bench_optimization()

    if args.profile:
        profile_optimization()

    all_pass = all(r[4] for r in bt_rows) and all(r[4] for r in opt_rows)
    print("\n" + "=" * 60)
    print(f"결과: {'모든 목표 충족 ✓' if all_pass else '일부 목표 미달 ✗'}")
    print("=" * 60)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
