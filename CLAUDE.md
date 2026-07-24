# QuantInvest_Tool - 개발 가이드

## 개요

**QuantInvest_Tool**은 정량적 투자 전략 분석 및 백테스팅을 위한 독립 실행형 GUI 애플리케이션입니다. 교육용 Jupyter 노트북을 금융 데이터의 트레이딩 전략 분석에 활용할 수 있는 접근성 높고 전문적인 도구로 변환합니다.

## 프로젝트 구조

```
QuantInvest_USA/
├── src/                           # 메인 애플리케이션 소스 코드
│   ├── __init__.py
│   ├── main.py                    # 애플리케이션 진입점
│   ├── ui/                        # PySide6 사용자 인터페이스
│   │   ├── __init__.py
│   │   ├── main_window.py         # 메인 애플리케이션 창
│   │   ├── dialogs.py             # 모달 대화 상자 및 차트
│   │   └── styles.py              # UI 테마 및 스타일링
│   ├── strategies/                # 트레이딩 전략 구현
│   │   ├── __init__.py
│   │   ├── base_strategy.py       # 추상 기본 클래스
│   │   ├── momentum_strategy.py    # 모멘텀 트레이딩 전략
│   │   ├── trend_following.py      # 추세 추종 전략
│   │   ├── mean_reversion.py       # 평균 회귀 전략
│   │   └── portfolio.py            # 포트폴리오 최적화 전략
│   ├── backtest/                  # 백테스팅 엔진
│   │   ├── __init__.py
│   │   ├── engine.py              # 메인 백테스팅 루프
│   │   ├── metrics.py             # 성과 지표 계산
│   │   └── optimizer.py           # 파라미터 그리드 서치 최적화기
│   ├── data/                      # 데이터 처리 계층
│   │   ├── __init__.py
│   │   ├── downloader.py          # yfinance 래퍼
│   │   └── cache.py               # SQLite 캐시 관리
│   └── utils/                     # 유틸리티 함수
│       ├── __init__.py
│       └── plotting.py            # Matplotlib 플로팅 유틸리티
│
├── tests/                         # 단위 및 통합 테스트
│   ├── __init__.py
│   └── test_strategies.py
│
├── samples/                       # 원본 Jupyter 노트북 예제
│   ├── ch_04/                     # 파이썬 기초
│   ├── ch_05/                     # 자료 구조
│   ├── ch_06/                     # 추세 추종
│   ├── ch_07/                     # 추세 추종 (심화)
│   ├── ch_08/                     # 모멘텀 전략
│   ├── ch_09/                     # 평균 회귀
│   ├── ch_10/                     # 포트폴리오 이론
│   └── ch_11/                     # 모멘텀 포트폴리오
│
├── .claude/                       # Claude Code 설정
│   └── settings.json
│
├── requirements.txt               # 파이썬 의존성
├── setup.py                       # 패키지 설정 및 배포
├── pyproject.toml                 # 최신 파이썬 프로젝트 설정
├── CLAUDE.md                      # 이 파일
├── ARCHITECTURE.md                # 시스템 아키텍처 및 흐름
├── TO_DO.md                       # 기능 로드맵
├── README.md                      # 사용자 문서
└── .gitignore                     # Git 설정
```

## 설치 안내

### 1. 환경 설정

**사전 요구 사항:**
- Python 3.12 이상 (3.12–3.14에서 검증됨)
- pip 패키지 관리자
- Windows (PyInstaller .exe 생성용)

**가상 환경 생성:**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

**의존성 설치:**
```bash
pip install -r requirements.txt
```

### 2. 애플리케이션 실행

**소스에서 실행 (개발):**
```bash
cd QuantInvest_USA
python src/main.py
```

**테스트 실행:**
```bash
pytest tests/ -v
pytest tests/ --cov=src  # 커버리지 리포트 포함
```

### 3. 실행 파일 빌드

**PyInstaller Spec 생성:**
```bash
pyinstaller --onefile --windowed --name "QuantInvest_Tool" \
    --icon=assets/icon.ico \
    src/main.py
```

**출력:** `dist/QuantInvest_Tool.exe`

## 아키텍처 개요

### 핵심 구성 요소

#### 1. 데이터 계층 (`src/data/`)
- **downloader.py**: yfinance API 래핑
  - `download_data(ticker, start_date, end_date)` - OHLCV 데이터 다운로드
  - 잘못된 티커 및 날짜 범위에 대한 오류 처리
  - 원시 데이터를 로컬에 캐싱
- **cache.py**: SQLite 데이터베이스 관리
  - `CacheManager` 클래스가 로컬 데이터베이스 읽기/쓰기를 처리
  - 날짜 범위 쿼리를 통해 중복 다운로드 방지
  - 테이블: `price_history` (ticker, date, OHLCV)

#### 2. 전략 계층 (`src/strategies/`)
- **base_strategy.py**: 추상 기본 클래스 `BaseStrategy`
  - 인터페이스: `calculate_signals()`, `run_backtest()`, `optimize_parameters()`
  - 공통 속성: initial_capital, transaction_fee

- **전략 구현:**
  - **momentum_strategy.py**: 가격 모멘텀 + 자금 흐름 지수(MFI) 필터
    - 파라미터: momentum_period, mfi_period, mfi_threshold, stop_loss
  - **trend_following.py**: 지수 이동 평균(EMA) 교차
    - 파라미터: short_window, long_window, stop_loss
  - **mean_reversion.py**: Z-점수 기반 평균 회귀 및 페어 트레이딩
    - 파라미터: lookback_period, z_score_threshold, position_size
  - **portfolio.py**: 상관관계 분석을 활용한 다종목 모멘텀
    - 파라미터: portfolio_size, momentum_period, weight_method

#### 3. 백테스팅 엔진 (`src/backtest/`)
- **engine.py**: 이벤트 기반 백테스팅 시뮬레이션
  - 시장 데이터를 순차적으로 처리
  - 현금 포지션, 보유 자산, 거래 이력 유지
  - 매수/매도 신호 및 시간 경과에 따른 성과 추적
  - 트레일링 스톱 로스 및 거래 수수료 지원

- **metrics.py**: 성과 분석 계산
  - CAGR: 연평균 복리 성장률
  - 샤프 비율: 위험 조정 수익률 (risk_free_rate = 0.3%)
  - 최대 낙폭(Maximum Drawdown): 최악의 고점 대비 저점 하락
  - 승률: 수익성 있는 거래의 비율
  - 손익비(Profit/Loss Ratio): 평균 이익 대 평균 손실
  - 칼마 비율(Calmar Ratio): 낙폭 단위당 수익

- **optimizer.py**: 파라미터 그리드 서치
  - 파라미터 범위에 대한 완전 탐색(brute-force)
  - 속도 향상을 위한 선택적 병렬 처리
  - 최적 파라미터 및 관련 지표 반환

#### 4. UI 계층 (`src/ui/`)
- **main_window.py**: PySide6 메인 애플리케이션 창
  - 탭 1: 종목 및 날짜 설정
  - 탭 2: 전략 선택 및 파라미터
  - 탭 3: 최적화 설정
  - 탭 4: 결과 및 분석

- **dialogs.py**: 모달 대화 상자 및 위젯
  - `DateRangeDialog`: 달력 기반 날짜 선택
  - `ParameterRangeDialog`: 최적화를 위한 범위 입력
  - `ChartDialog`: 임베디드 matplotlib 그림 뷰어
  - `ProgressDialog`: 비차단(non-blocking) 최적화 진행 상황

- **styles.py**: PySide6 스타일시트 적용
  - 전문적인 라이트 및 다크 테마
  - 일관된 색상 구성, 폰트, 간격

#### 5. 유틸리티 (`src/utils/`)
- **plotting.py**: Matplotlib 통합
  - `plot_cumulative_returns()`: 전략 대 매수 후 보유(buy&hold) 비교
  - `plot_indicators()`: 가격 + 기술적 지표
  - `plot_buy_sell_signals()`: 진입/청산 지점 시각화
  - `embed_plot_in_qt()`: FigureCanvas 임베딩

## 코드 패턴 및 관례

### 전략 구현 패턴
```python
class CustomStrategy(BaseStrategy):
    def __init__(self, initial_capital=10000, transaction_fee=0.001):
        super().__init__(initial_capital, transaction_fee)
        self.params = {}  # 사용자가 설정한 파라미터
    
    def calculate_signals(self, data):
        """Return DataFrame with 'Signal' column (-1, 0, 1)"""
        pass
    
    def run_backtest(self, data):
        """Return DataFrame with 'Cumulative_Return' column"""
        pass
    
    def optimize_parameters(self, data, param_ranges):
        """Grid search over param_ranges, return optimal params"""
        pass
```

### 백테스팅 루프 패턴
```python
for i in range(1, len(data)):
    price = data['Close'].iloc[i]
    signal = data['Signal'].iloc[i]
    
    if position == 0 and signal == 1:  # 매수 신호
        execute_buy(price, cash, ...)
    elif position == 1 and signal == -1:  # 매도 신호
        execute_sell(price, ...)
    
    portfolio_value[i] = cash + holdings * price
```

### PySide6 시그널-슬롯 패턴
```python
# PySide6는 pyqtSignal 대신 Signal, exec_() 대신 exec() 를 사용한다.
from PySide6.QtCore import QObject, Signal, QThread

self.backtest_button.clicked.connect(self.on_backtest_clicked)

def on_backtest_clicked(self):
    # UI 응답성 유지를 위해 워커(QObject)를 QThread로 이동시켜 실행.
    # 워커/스레드는 인스턴스 속성으로 보관해 GC로 파괴되지 않게 한다.
    self.worker.moveToThread(self.thread)
    self.thread.started.connect(self.worker.run)
    self.thread.start()
```

## 데이터 흐름

1. **사용자 입력** → 종목 티커, 날짜 범위, 전략, 파라미터
2. **데이터 계층** → yfinance 또는 SQLite 캐시에서 가져오기
3. **전략** → 기술적 지표 및 신호 계산
4. **백테스트 엔진** → 트레이딩 시뮬레이션, 성과 추적
5. **지표** → CAGR, 샤프, MDD 등 계산
6. **시각화** → 누적 수익률, 매수/매도 지점 플로팅
7. **내보내기** → 결과를 CSV/Excel로 저장

## 테스트 전략

### 단위 테스트
- 개별 전략 구현
- 노트북 결과와 대조한 지표 계산
- 캐시 작업

### 통합 테스트
- 엔드투엔드 백테스트 워크플로우
- 전략 최적화 수렴
- UI 대화 상자 상호작용

### 성능 테스트
- 큰 파라미터 범위에 대한 최적화 속도
- 긴 날짜 범위에서의 메모리 사용량
- 대용량 데이터셋의 차트 렌더링

## 일반 작업

### 새 전략 추가하기
1. `BaseStrategy`를 확장하는 클래스로 `strategies/new_strategy.py` 생성
2. `calculate_signals()` 및 `run_backtest()` 메서드 구현
3. 해당 노트북 예제에서 로직 추출
4. `tests/test_strategies.py`에 단위 테스트 추가
5. `src/ui/main_window.py`의 전략 드롭다운에 등록
6. 애플리케이션에서 엔드투엔드 테스트

### 백테스팅 로직 수정하기
1. `src/backtest/engine.py`의 관련 메서드 편집
2. `src/backtest/metrics.py`의 지표 계산 업데이트
3. 노트북 예제와 결과 비교
4. 단위 테스트를 실행하여 검증

### UI 레이아웃 변경하기
1. `src/ui/main_window.py`의 탭 및 위젯 편집
2. 필요 시 `src/ui/styles.py`의 스타일링 조정
3. `src/ui/dialogs.py`의 대화 상자 정의 업데이트
4. 다양한 창 크기에서 반응형 레이아웃 테스트

## 성능 최적화

### 데이터 캐싱
- SQLite가 과거 데이터를 로컬에 저장
- 동일한 종목/날짜의 후속 실행은 캐시를 사용
- UI에서 수동 캐시 삭제 옵션 제공

### 파라미터 최적화
- 그리드 서치는 큰 범위에서 느릴 수 있음
- 선택 사항: `optimizer.py`에서 멀티프로세싱 활성화
- 대화 상자를 통해 사용자에게 진행 상황 피드백 제공

### 시각화
- Qt에 최적화된 Matplotlib 백엔드 사용
- 탭에 접근할 때만 차트를 지연 로딩(lazy-load)
- 성능을 위해 차트 해상도 제한

## 디버깅 팁

### 로깅
- 거래 추적을 위해 `src/backtest/engine.py`에 로깅 추가
- yfinance 다운로드 시도 및 캐시 적중 로깅
- 상세 출력을 위해 `src/main.py`에서 디버그 모드 활성화

### 자주 발생하는 문제
- **yfinance 다운로드 실패**: 인터넷, 티커 심볼, 날짜 범위 확인
- **잘못된 전략 파라미터**: 최적화기로 보내기 전에 UI에서 범위 검증
- **PyInstaller .exe 실행 실패**: 모든 임포트가 `requirements.txt`에 있는지 확인

## 릴리스 빌드

1. `setup.py`에서 버전 업데이트
2. 모든 테스트 실행: `pytest tests/ -v`
3. .exe 생성: `pyinstaller QuantInvest.spec`
4. 파이썬이 없는 깨끗한 머신에서 .exe 테스트
5. .exe 첨부와 함께 GitHub 릴리스 생성

## 의존성

| Package | Purpose | Version constraint | Latest verified |
|---------|---------|--------------------|-----------------|
| yfinance | 주식 데이터 다운로드 | >=1.5.2,<2 | 1.5.2 |
| pandas | 데이터 조작 | >=3.0,<4 | 3.0.5 |
| numpy | 수치 연산 | >=2.3,<3 | 2.5.1 |
| ta | 기술적 지표 | >=0.11,<1 | 0.11.0 |
| statsmodels | 통계 분석 | >=0.14.5,<0.15 | 0.14.6 |
| scipy | 과학 연산 | >=1.16,<2 | 1.18.0 |
| matplotlib | 시각화 | >=3.10.5,<4 | 3.11.1 |
| PySide6 | GUI 프레임워크 (Qt 공식, LGPL v3) | >=6.11,<7 | 6.11.1 |
| PyInstaller | .exe 패키징 | >=6.16,<7 | 6.21.0 |

> **버전 정책:** 하한선(floor)은 현재 테스트를 거친 안정 릴리스에 고정되며, 업그레이드가
> 안전하도록 다음 메이저 버전 아래로 상한을 둡니다. Python 3.12–3.14에서 확인되었습니다
> (컴파일된 패키지는 `cp314` 휠을 제공하며, PySide6 6.11.1은 `requires-python <3.15,>=3.10`과
> 3.14에 설치되는 `cp310-abi3` 휠을 가집니다).
> yfinance 0.2.40 → 1.x 전환은 `multi_level_index` / `auto_adjust` / `progress`
> 다운로드 파라미터를 그대로 유지하므로 기존 다운로드 코드는 변경되지 않습니다.

## 참고 자료

- **노트북**: 전략 구현 참조는 `samples/` 참고
- **PySide6 문서**: https://doc.qt.io/qtforpython-6/
- **yfinance 문서**: https://github.com/ranaroussi/yfinance
- **pandas 문서**: https://pandas.pydata.org/docs/

---

**최종 업데이트**: 2026-07-24
**관리자**: 개발팀
