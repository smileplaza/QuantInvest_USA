# 노트북 대비 검증 결과 (Notebook Parity Report)

**작성일**: 2026-07-24
**대상**: `src/strategies/*` vs `samples/ch_*`
**테스트**: `tests/test_notebook_parity.py`, `tests/test_edge_cases.py`

---

## 요약

원본 교육용 노트북의 전략 로직을 src 구현이 얼마나 충실히 재현하는지 검증했다.
검증 과정에서 **실제 버그 1건을 발견·수정**했으며, 4개 전략의 재현 수준을 분류했다.

| 전략 | 원본 노트북 | 재현 수준 | 비고 |
|------|-----------|----------|------|
| 추세추종 | ch_06, ch_07 | ✅ **정확 재현** (< 0.1%, 실측 ~1e-12) | adjust=False 버그 수정 후 |
| 모멘텀 | ch_08 | 🟡 신호 로직 일치 / 확장 구현 | MFI 필터·신호청산 추가(의도적) |
| 평균회귀 | ch_09 | 🔵 단순화 구현 | 노트북=페어트레이딩, src=단일종목 Z-score |
| 포트폴리오 | ch_10, ch_11 | 🔵 단순화 구현 | 노트북=다종목, src=단일 모멘텀 프록시 |

---

## 🐛 발견·수정한 버그

### EMA 계산의 `adjust` 파라미터 불일치 (추세추종)

**위치**: `src/strategies/trend_following.py` `calculate_signals()`

**문제**:
```python
# 수정 전 (기본값 adjust=True — 가중 평균식 EMA)
data['Short_EMA'] = data['Close'].ewm(span=short_window).mean()

# 수정 후 (adjust=False — 표준 재귀식 EMA, 노트북과 일치)
data['Short_EMA'] = data['Close'].ewm(span=short_window, adjust=False).mean()
```

원본 노트북(ch_06 cell 8)은 `ewm(span=N, adjust=False)`를 사용한다.
`adjust=True`(pandas 기본값)와 `adjust=False`는 **서로 다른 EMA 값**을 산출하여
골든/데드 크로스 시점이 달라지고, 결과적으로 매매 신호와 누적 수익률이 어긋난다.

**영향**: 수정 전에는 src 추세추종 결과가 노트북과 미세하게 불일치했다.
`adjust=False`는 대부분의 트레이딩 문헌에서 사용하는 표준 EMA 관례이기도 하다.

**검증**: 수정 후 `test_cumulative_return_matches_notebook`이 3개 파라미터
조합(10/20, 12/26, 5/40)에서 노트북 참조 구현과 기계 정밀도 수준으로 일치.

---

## 전략별 상세

### ✅ 추세추종 (ch_06/07) — 정확 재현

노트북 알고리즘을 테스트에 그대로 재구현(`_reference_trend_following`)하고,
src를 동일 조건(수수료 0, 손절 미발동)으로 맞춰 대조.

- EMA 크로스오버 신호 생성: 완전 일치
- 이벤트 기반 백테스트(정수 주식 수, 현금 관리): 완전 일치
- 누적 수익률: `rel < 1e-3` (실측 ~1e-12)

**의도된 차이(설정으로 흡수)**: src는 거래 수수료(기본 0.1%)와 트레일링 손절을
추가 지원한다. 노트북에는 없는 기능이므로 검증 시 fee=0, stop_loss=대형값으로 무력화.

### 🟡 모멘텀 (ch_08) — 신호 로직 일치, 확장 구현

노트북의 실행 전략은 `mom_strategy1(df, 12, 0.07)`이며:
- **MFI 필터를 사용하지 않는다** (MFI는 별도 셀에서 시각화용으로만 계산).
- **손절로만 청산**한다 (모멘텀이 음전환해도 보유 유지).

src `MomentumStrategy`는 여기에 **MFI 필터**와 **신호 기반 청산**을 추가한
확장 버전이다. 따라서 백테스트 결과의 정확 재현은 대상이 아니며, 두 구현이
공유하는 **모멘텀 부호 → 포지션** 신호 생성부만 대조하여 일치를 확인했다
(`test_momentum_position_matches_notebook`, 일치율 ≥ 98%).

> 향후 노트북과 완전 일치가 필요하면 MFI 필터를 옵션화(기본 off)하고
> 신호 기반 청산을 토글 가능하게 만드는 방안을 검토할 수 있다.

### 🔵 평균회귀 (ch_09) — 단순화 구현

- **노트북**: 두 종목(PEP/MCD) **페어 트레이딩**. 롤링 OLS 회귀로 베타 추정,
  스프레드의 Z-score로 롱/숏 진입, 베타 헤지 포지션.
- **src**: **단일 종목** Z-score 평균회귀 (종가 vs 자기 롤링 평균/표준편차).

교육용 단일 종목 버전으로 의도적으로 단순화한 구현이다. 알고리즘 구조가 달라
정확 재현 대상이 아니다.

### 🔵 포트폴리오 (ch_10/11) — 단순화 구현

- **노트북**: 다종목 포트폴리오(효율적 프론티어, 베타, 다종목 모멘텀 랭킹).
- **src**: 단일 Close 계열에 대한 모멘텀 프록시.

마찬가지로 단일 종목 프레임에 맞춘 단순화 구현.

---

## 엣지 케이스 방어 (tests/test_edge_cases.py)

검증 중 함께 강화한 비정상 입력 방어 로직 (14개 테스트):

| 엣지 케이스 | 처리 |
|-----------|------|
| 극단 파라미터(기간 ≥ 데이터 길이) | `InsufficientDataError` 발생 (크래시 방지) |
| 거래량 전부 0 | MFI NaN → 명확한 예외 또는 안전 처리 |
| 단일 행 데이터 | `InsufficientDataError` |
| 최적화 전 조합 실패 | `InsufficientDataError` (기존: `None.copy()` 크래시) |
| 빈 데이터 지표 계산 | 0 지표 dict 반환 (기존: `IndexError`) |
| 초단기 기간 CAGR | 연율화 생략, 오버플로 방지 |
| 가격 변동 0(변동성 0) | 샤프 0, 전 지표 유한 |

관련 수정 파일:
- `src/strategies/base_strategy.py` — `InsufficientDataError`, `_validate_backtest_data()`, 최적화 None 방어
- `src/strategies/{momentum,trend_following,mean_reversion,portfolio}.py` — run_backtest 진입 검증
- `src/backtest/metrics.py` — 빈 데이터 방어, CAGR 오버플로 방어

---

## 결론

- **추세추종**은 노트북과 정확히 일치함이 자동 테스트로 보증된다.
- 나머지 전략은 교육 목적의 단순화/확장 구현으로, 그 차이가 **문서화**되었다.
- 엣지 케이스 방어로 비정상 입력에서의 크래시가 제거되었다.
- 전체 테스트 **103개 통과**.
