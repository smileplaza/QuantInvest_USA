"""
노트북 대비 검증 (Notebook Parity)

원본 Jupyter 노트북(samples/ch_*)의 참조 알고리즘을 테스트 내에 그대로
재구현하고, src 구현이 동일 합성 데이터에서 동일한 결과를 산출하는지
0.1% 이내로 검증한다.

목적: src 리팩터링이 교육용 노트북의 전략 로직을 충실히 재현함을 보증.

주의 — 노트북과 src의 알려진(의도된) 차이:
- 거래 수수료: src는 설정 가능(기본 0.1%). 검증 시 fee=0으로 맞춘다.
- 손절(stop loss): src는 트레일링 손절 지원. 추세추종 검증에서는 stop_loss를
  매우 크게 설정해 발동하지 않도록 한다.
- 모멘텀 전략(ch_08): 노트북의 실행 전략 `mom_strategy1`은 MFI 필터를 사용하지
  않고 손절로만 청산한다. src 모멘텀은 MFI 필터 + 신호 기반 청산을 추가한
  확장판이므로 정확 재현 대상이 아니다(별도 문서화). 여기서는 노트북과 src가
  공유하는 '모멘텀 부호 → 포지션' 신호 생성 로직만 대조한다.
"""

import numpy as np
import pandas as pd
import pytest

from strategies.trend_following import TrendFollowingStrategy
from strategies.momentum_strategy import MomentumStrategy


# 손절이 절대 발동하지 않도록 하는 큰 값 (entry*(1-10) < 0)
NEVER_STOP = 10.0
PARITY_TOL = 1e-3  # 0.1%


def _reference_trend_following(df, short_window, long_window, cash_init=10000):
    """원본 노트북 ch_06 cell 8 알고리즘의 정확한 재구현 (수수료/손절 없음).

    src TrendFollowingStrategy 와 동일한 '전 구간' 백테스트(초기 warm-up
    트리밍 없이)로 맞춰 순수 알고리즘 동등성을 검증한다.
    """
    data = df.copy()
    data['Short_MA'] = data['Close'].ewm(span=short_window, adjust=False).mean()
    data['Long_MA'] = data['Close'].ewm(span=long_window, adjust=False).mean()
    data['Position'] = np.where(data['Short_MA'] > data['Long_MA'], 1, 0)
    data['Signal'] = data['Position'].diff().fillna(0)

    cash = cash_init
    asset = np.zeros(len(data))
    asset[0] = cash
    pos = 0
    num = 0
    prices = data['Close'].values
    signals = data['Signal'].values

    for i in range(1, len(data)):
        if pos == 0:
            if signals[i] == 1:  # 골든 크로스 → 매수
                pos = 1
                entry_price = prices[i]
                num = int(cash / entry_price)
                cash -= entry_price * num
        elif pos == 1:
            if signals[i] == -1:  # 데드 크로스 → 매도
                pos = 0
                cash += prices[i] * num
        asset[i] = cash if pos == 0 else cash + prices[i] * num

    return asset[-1] / cash_init


class TestTrendFollowingParity:
    """추세추종 전략: 노트북 ch_06 대비 정확 재현"""

    @pytest.mark.parametrize("short_w,long_w", [(10, 20), (12, 26), (5, 40)])
    def test_cumulative_return_matches_notebook(self, sample_data, short_w, long_w):
        # 참조(노트북) 결과
        ref_final = _reference_trend_following(sample_data, short_w, long_w)

        # src 결과: 수수료 0, 손절 미발동으로 맞춤
        strat = TrendFollowingStrategy(initial_capital=10000, transaction_fee=0.0)
        strat.params = {'short_window': short_w, 'long_window': long_w, 'stop_loss': NEVER_STOP}
        signals = strat.calculate_signals(sample_data)
        result = strat.run_backtest(signals)
        src_final = result['Cumulative_Return'].iloc[-1]

        assert src_final == pytest.approx(ref_final, rel=PARITY_TOL), (
            f"추세추종 불일치: src={src_final:.6f}, notebook={ref_final:.6f} "
            f"(short={short_w}, long={long_w})"
        )

    def test_ema_uses_adjust_false(self, sample_data):
        # 회귀 방지: src EMA가 노트북과 동일한 adjust=False 재귀식이어야 함
        strat = TrendFollowingStrategy()
        strat.params = {'short_window': 10, 'long_window': 20, 'stop_loss': 0.07}
        result = strat.calculate_signals(sample_data)

        expected_short = sample_data['Close'].ewm(span=10, adjust=False).mean()
        # calculate_signals가 반환한 Short_EMA 와 adjust=False EMA가 일치
        np.testing.assert_allclose(
            result['Short_EMA'].values, expected_short.values, rtol=1e-9
        )


def _reference_momentum_signals(df, period):
    """노트북 ch_08 mom_strategy1 의 신호 생성부(모멘텀 부호 → 포지션)."""
    data = df.copy()
    data['Mom'] = data['Close'].pct_change(periods=period)
    data.dropna(inplace=True)
    mom_pos = pd.Series(np.where(data['Mom'] > 0, 1, 0), index=data.index)
    mom_signals = mom_pos.diff().fillna(0)
    return mom_pos, mom_signals


class TestMomentumSignalParity:
    """모멘텀 전략: 노트북과 공유하는 신호 생성 로직 대조.

    (MFI 필터를 무력화하여 순수 모멘텀 부호 신호만 비교)
    """

    def test_momentum_position_matches_notebook(self, sample_data):
        period = 12
        ref_pos, _ = _reference_momentum_signals(sample_data, period)

        # MFI 임계값을 0으로 낮춰 필터가 항상 통과하도록 → 순수 모멘텀 신호
        strat = MomentumStrategy()
        strat.params = {'momentum_period': period, 'mfi_period': 7, 'mfi_level': 0.0, 'stop_loss': 0.07}
        result = strat.calculate_signals(sample_data)

        # 공통 인덱스에서 Position(모멘텀 부호) 비교
        common = ref_pos.index.intersection(result.index)
        assert len(common) > 0
        # src Position은 momentum>0 AND mfi>0 이므로, mfi_level=0에서 모멘텀 부호와 동일해야 함
        ref_aligned = ref_pos.loc[common].values
        src_aligned = result.loc[common, 'Position'].values
        match_rate = np.mean(ref_aligned == src_aligned)
        # MFI가 정확히 0인 극단 케이스를 제외하면 거의 100% 일치
        assert match_rate >= 0.98, f"모멘텀 포지션 일치율 {match_rate:.1%}"
