# QuantInvest Tool - 상세 GUI 아키텍처

## 목차
1. [개요](#개요)
2. [위젯 계층 구조](#위젯-계층-구조)
3. [탭별 설계](#탭별-설계)
4. [상태 관리](#상태-관리)
5. [신호/슬롯 아키텍처](#신호슬롯-아키텍처)
6. [스레딩 통합](#스레딩-통합)
7. [데이터 흐름](#데이터-흐름)
8. [에러 처리](#에러-처리)
9. [스타일링 & 테마](#스타일링--테마)
10. [상호작용 흐름](#상호작용-흐름)

---

## 개요

QuantInvest Tool GUI는 **PySide6**를 사용하여 탭 기반 인터페이스로 구축되었습니다. 데이터 입력, 전략 구성, 최적화 설정, 결과 분석이 명확하게 분리되어 있습니다. 아키텍처는 워커 스레드를 통한 반응성과 실시간 피드백을 강조합니다.

### 설계 철학
- **모듈식**: 각 탭은 독립적이지만 애플리케이션 상태를 공유
- **반응형**: 장시간 작업은 백그라운드 스레드에서 실행
- **명확한 피드백**: 실시간 진행률, 에러 메시지, 상태 업데이트
- **전문적**: 깔끔하고 정리된 직관적 인터페이스

---

## 위젯 계층 구조

### 애플리케이션 위젯 트리

```
QApplication
    │
    └─ QMainWindow (MainWindow - 메인 창)
        │
        ├─ QMenuBar (메뉴 바)
        │   ├─ 파일 메뉴
        │   │   ├─ 새 세션
        │   │   ├─ 세션 열기
        │   │   ├─ 세션 저장
        │   │   ├─ 결과 내보내기
        │   │   └─ 종료
        │   └─ 도움말 메뉴
        │       ├─ 정보
        │       ├─ 문서
        │       └─ 설정
        │
        ├─ QToolBar (도구 모음 - 선택사항)
        │   ├─ 빠른 실행 버튼
        │   ├─ 중지 버튼
        │   └─ 캐시 삭제 버튼
        │
        ├─ QWidget (중앙 위젯)
        │   │
        │   ├─ QVBoxLayout
        │   │   │
        │   │   ├─ QTabWidget (탭 컨테이너)
        │   │   │   │
        │   │   │   ├─ 탭 0: 주식 설정
        │   │   │   │   └─ StockConfigWidget
        │   │   │   │
        │   │   │   ├─ 탭 1: 전략 선택
        │   │   │   │   └─ StrategySelectionWidget
        │   │   │   │
        │   │   │   ├─ 탭 2: 최적화 설정
        │   │   │   │   └─ OptimizationWidget
        │   │   │   │
        │   │   │   └─ 탭 3: 결과 & 분석
        │   │   │       └─ ResultsAnalysisWidget
        │   │   │
        │   │   └─ QFrame (상태/제어 바)
        │   │       ├─ QProgressBar
        │   │       ├─ QLabel (상태 메시지)
        │   │       └─ QPushButton (취소)
        │   │
        │   └─ QStatusBar (상태 표시줄)
        │       ├─ QLabel (왼쪽: 세션 이름)
        │       ├─ QLabel (중간: 작업 상태)
        │       └─ QLabel (오른쪽: 캐시 상태)
        │
        └─ Worker Threads (백그라운드)
            ├─ DataDownloadWorker (데이터 다운로드)
            ├─ BacktestWorker (백테스트 실행)
            └─ OptimizationWorker (최적화 실행)
```

### 클래스 구조

```python
# 메인 애플리케이션 클래스

QMainWindow
    └─ MainWindow (메인 창)
        ├─ 모든 탭 관리
        ├─ 탭 간 통신 처리
        ├─ 워커 스레드 생성
        └─ 애플리케이션 상태 조정

QWidget
    ├─ StockConfigWidget (주식 설정 탭)
    │   ├─ 주식 입력 필드
    │   ├─ 날짜 범위 선택자
    │   └─ 데이터 검증 로직
    │
    ├─ StrategySelectionWidget (전략 선택 탭)
    │   ├─ 전략 드롭다운
    │   ├─ 동적 파라미터 입력
    │   └─ 검증 로직
    │
    ├─ OptimizationWidget (최적화 탭)
    │   ├─ 활성화/비활성화 체크박스
    │   ├─ 파라미터 범위 입력
    │   └─ 최적화 제어
    │
    └─ ResultsAnalysisWidget (결과 분석 탭)
        ├─ 지표 표
        ├─ 차트 표시 영역
        └─ 내보내기 버튼

QThread (워커)
    ├─ DataDownloadWorker
    ├─ BacktestWorker
    └─ OptimizationWorker
```

---

## 탭별 설계

### 탭 0: 주식 설정

**목적**: 주식 데이터 다운로드 및 준비

**레이아웃**:
```
┌─────────────────────────────────────────────────────┐
│ 주식 & 날짜 설정                                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 주식 선택:                                          │
│  ┌────────────────────────────────────────────┐   │
│  │ 주식 티커 (예: AAPL, MSFT, TSLA)         │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
│ 날짜 범위:                                          │
│  ┌──────────────────┐  ┌──────────────────┐      │
│  │ 시작 날짜        │  │ 종료 날짜        │      │
│  │ [2023-01-01] ▼  │  │ [2024-01-01] ▼   │      │
│  └──────────────────┘  └──────────────────┘      │
│                                                     │
│  ☑ 캐시 데이터 사용 (사용 가능한 경우)            │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │      [Yahoo Finance에서 데이터 다운로드]     │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
│ 데이터 미리보기:                                    │
│  ┌────────────────────────────────────────────┐   │
│  │ 티커: AAPL                                  │   │
│  │ 날짜 범위: 2023-01-01 ~ 2024-01-01        │   │
│  │ 거래일: 252일                              │   │
│  │ 로드됨: OHLCV 데이터 4,500행               │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**컴포넌트**:
```python
class StockConfigWidget(QWidget):
    # 입력 필드
    stock_input = QLineEdit()           # 티커 기호
    start_date = QDateEdit()            # 시작 날짜
    end_date = QDateEdit()              # 종료 날짜
    use_cache_checkbox = QCheckBox()    # 캐시 사용 여부
    
    # 버튼
    fetch_button = QPushButton("데이터 다운로드")
    clear_cache_button = QPushButton("캐시 삭제")
    
    # 표시 영역
    preview_label = QLabel()            # 데이터 미리보기
    status_label = QLabel()             # 상태 메시지
    progress_bar = QProgressBar()       # 다운로드 진행률
    
    # 신호
    data_ready = Signal(pd.DataFrame)
    download_started = Signal()
    error_occurred = Signal(str)
```

**작업 흐름**:
1. 사용자가 티커 기호 입력
2. 사용자가 날짜 범위 선택
3. "데이터 다운로드" 클릭
   - 캐시에서 데이터 확인
   - 캐시 히트: SQLite에서 로드
   - 캐시 미스: Yahoo Finance에서 다운로드
   - 캐시에 저장
   - 미리보기 표시
   - 신호 발송하여 다음 탭 활성화

**검증**:
- 티커 길이: 1-5자
- 날짜 범위: end_date > start_date
- 날짜 범위: 30년 이상 불가
- 티커 형식: 영숫자만

---

### 탭 1: 전략 선택 & 파라미터

**목적**: 거래 전략 구성 및 파라미터 설정

**레이아웃**:
```
┌─────────────────────────────────────────────────────┐
│ 전략 선택 & 파라미터                                │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 전략 선택:                                          │
│  ┌──────────────────────────────────────────────┐  │
│  │ 전략: [모멘텀 ▼]                            │  │
│  │ 설명: 가격 모멘텀을 기반으로 거래...        │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│ 전략 파라미터:                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ 모멘텀 기간: [12         ] (3-30)            │  │
│  │ MFI 수준:    [46.5   ▬▬▬▬▬▬▬▬] (20-80)   │  │
│  │ 손절 비율:   [7%         ] (1%-20%)          │  │
│  │                                              │  │
│  │ ⓘ 모멘텀 기간: 모멘텀 계산 일 수 (3-30)  │  │
│  │ ⓘ MFI 수준: 머니 플로우 인덱스 임계값   │  │
│  │ ⓘ 손절 비율: 손실 한도 (%)             │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ☑ 기본값 사용  ☑ 고급 설정                        │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  [기본값으로 재설정] [파라미터 검증]         │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│ 파라미터 사전: [사전으로 저장] [사전 로드]         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**전략 파라미터 정의**:

```python
STRATEGY_PARAMS = {
    "모멘텀": {
        "momentum_period": {"type": "int", "min": 3, "max": 30, "default": 12},
        "mfi_level": {"type": "float", "min": 20, "max": 80, "default": 46.5},
        "stop_loss": {"type": "float", "min": 0.01, "max": 0.20, "default": 0.07}
    },
    "추세 추종": {
        "short_window": {"type": "int", "min": 5, "max": 30, "default": 12},
        "long_window": {"type": "int", "min": 20, "max": 100, "default": 26},
        "stop_loss": {"type": "float", "min": 0.01, "max": 0.20, "default": 0.07}
    },
    "평균 회귀": {
        "lookback_period": {"type": "int", "min": 5, "max": 50, "default": 20},
        "z_score": {"type": "float", "min": 0.5, "max": 3.0, "default": 1.96},
        "position_size": {"type": "float", "min": 0.01, "max": 1.0, "default": 0.5}
    },
    "포트폴리오": {
        "portfolio_size": {"type": "int", "min": 2, "max": 10, "default": 5},
        "correlation_filter": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.7},
        "weight_method": {"type": "choice", "options": ["동일", "시가총액", "역분산"], "default": "동일"}
    }
}
```

**작업 흐름**:
1. 사용자가 드롭다운에서 전략 선택
2. 설명 및 파라미터 동적 표시
3. 사용자가 파라미터 조정 또는 기본값 사용
4. "파라미터 검증" 클릭
5. 유효성 검사 (최소/최대 제약 확인)
6. 유효함: 다음 탭 활성화
7. 유효하지 않음: 에러 메시지 표시

---

### 탭 2: 최적화 설정

**목적**: 파라미터 검색 범위 구성

**레이아웃**:
```
┌─────────────────────────────────────────────────────┐
│ 파라미터 최적화 설정                                │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ☐ 파라미터 최적화 활성화                           │
│                                                     │
│ 파라미터 검색 범위:                                 │
│ ┌──────────────────────────────────────────────┐   │
│ │ 모멘텀 기간:   [3  ...  30] 단계 1            │   │
│ │ MFI 수준:      [20 ...  80] 단계 5            │   │
│ │ 손절 비율:     [1% ... 20%] 단계 1%           │   │
│ │                                              │   │
│ │ 예상 조합: 28 × 13 × 20 = 7,280              │   │
│ │ 예상 시간: ~10-15분                           │   │
│ └──────────────────────────────────────────────┘   │
│                                                     │
│ 최적화 옵션:                                        │
│  ☑ 병렬 처리  [스레드: 4  ▼]                      │
│  ☑ 진행률 표시  ☑ 자동 최선 선택                  │
│                                                     │
│ 제약 조건:                                          │
│  ☐ 최소 연간 수익:    [0%]                        │
│  ☐ 최대 낙폭:         [50%]                       │
│  ☐ 최소 승률:         [0%]                        │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │   [범위 재설정] [최적화 시작]              │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**컴포넌트**:
```python
class OptimizationWidget(QWidget):
    # 활성화/비활성화
    enable_checkbox = QCheckBox("파라미터 최적화 활성화")
    
    # 파라미터 범위
    range_widgets = []                  # 범위 입력 쌍 목록
    range_layout = QFormLayout()        # 범위 입력 그리드
    
    # 표시
    combination_label = QLabel()        # 조합 수
    time_estimate_label = QLabel()      # 시간 추정
    
    # 옵션
    parallel_checkbox = QCheckBox("병렬 처리")
    thread_spinbox = QSpinBox()         # 스레드 수
    progress_checkbox = QCheckBox("진행률 표시")
    auto_select_checkbox = QCheckBox("자동 최선 선택")
    
    # 제약 조건
    min_return_spinbox = QDoubleSpinBox()
    max_drawdown_spinbox = QDoubleSpinBox()
    min_win_rate_spinbox = QDoubleSpinBox()
    
    # 버튼
    reset_button = QPushButton("범위 재설정")
    start_button = QPushButton("최적화 시작")
    
    # 신호
    optimization_started = Signal(dict)
    optimization_progress = Signal(int, int)  # current, total
    optimization_complete = Signal(dict)
    error_occurred = Signal(str)
```

**작업 흐름**:
1. 사용자가 최적화 체크박스 활성화
2. 파라미터 범위가 기본값에서 자동으로 채워짐
3. 사용자가 범위 조정
4. 시스템이 조합 수 & 시간 추정 계산
5. 사용자가 선택 제약 조건 설정
6. "최적화 시작" 클릭
7. 백그라운드 워커가 그리드 검색 실행
8. 실시간 진행률로 최선 파라미터 표시
9. 완료 시 탭 4로 자동 전환

---

### 탭 3: 결과 & 분석

**목적**: 백테스트 결과 표시 및 분석

**레이아웃**:
```
┌─────────────────────────────────────────────────────┐
│ 결과 & 분석                                         │
├───────────────┬─────────────────────────────────────┤
│ 지표 표       │ 차트 탭                              │
├───────────────┼─────────────────────────────────────┤
│               │ [누적 수익] [지표]                 │
│ CAGR      38% │ [매수/매도] [낙폭]                 │
│ Sharpe    1.46│                                     │
│ MDD      -33% │ ┌─────────────────────────────────┐│
│ 승률      50% │ │                                 ││
│ P/L 비율  4.9 │ │    누적 수익 차트               ││
│               │ │                                 ││
│ 거래       │ │    ┌───────────────────────────┐ ││
│ 매수  10    │ │    │ 5배 ─────────────────────┐ │ ││
│ 매도  10    │ │    │    │        ┌────────── │ │ ││
│ 수익  10    │ │    │ 2배 ┤────────┤          │ │ ││
│ 손실   0    │ │    │    │        └──────────┤ │ ││
│               │ │    │ 1배 ├────────────────────┤ │ ││
│ [지표 복사]  │ │    │    │◆ 매수 ▼ 매도     │ │ ││
│               │ │    └────┴──────────────────────┘ ││
│               │ │    2023-01         2024-01       ││
│               │ └─────────────────────────────────┘│
│               │                                     │
│               │ [CSV 내보내기] [차트 내보내기]    │
│               │ [PDF 보고서 생성]                 │
│               │                                     │
└───────────────┴─────────────────────────────────────┘
```

**표시 지표**:
```python
# 지표 테이블 데이터
metrics_data = [
    ("전략", "모멘텀"),
    ("주식", "AAPL"),
    ("기간", "2023-01-01 ~ 2024-01-01"),
    ("", ""),  # 구분선
    ("CAGR", "38.37%"),
    ("샤프 지수", "1.46"),
    ("최대 낙폭", "-32.87%"),
    ("승률", "50.00%"),
    ("수익/손실 비율", "4.92"),
    ("", ""),  # 구분선
    ("총 거래", "20"),
    ("수익 거래", "10"),
    ("손실 거래", "10"),
    ("평균 수익", "24.9%"),
    ("평균 손실", "-5.1%"),
    ("평균 보유 기간", "47.5일"),
]
```

---

## 상태 관리

### 애플리케이션 상태 모델

```python
class ApplicationState:
    """모든 탭의 중앙 상태 관리"""
    
    # 주식 데이터
    stock_ticker: str = None
    start_date: QDate = None
    end_date: QDate = None
    stock_data: pd.DataFrame = None
    
    # 전략 구성
    strategy_name: str = "모멘텀"
    strategy_params: Dict[str, float] = {}
    
    # 최적화 설정
    optimization_enabled: bool = False
    optimization_params: Dict[str, Tuple[float, float]] = {}
    optimization_constraints: Dict[str, float] = {}
    
    # 결과
    backtest_results: Dict = None
    performance_metrics: Dict = None
    optimal_params: Dict = None
    
    # UI 상태
    current_tab: int = 0
    last_operation: str = None
    error_message: str = None
```

### 탭 간 상태 공유

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 공유 상태 생성
        self.state = ApplicationState()
        
        # 탭 생성
        self.stock_config_tab = StockConfigWidget(self.state)
        self.strategy_tab = StrategySelectionWidget(self.state)
        self.optimization_tab = OptimizationWidget(self.state)
        self.results_tab = ResultsAnalysisWidget(self.state)
        
        # 상태 변경 연결
        self.stock_config_tab.data_ready.connect(self.on_data_loaded)
        self.strategy_tab.parameters_validated.connect(self.on_params_validated)
        self.optimization_tab.optimization_complete.connect(self.on_optimization_complete)
        
        # 상태에 따라 탭 활성화/비활성화
        self.update_tab_availability()
```

---

## 신호/슬롯 아키텍처

### 신호 흐름 다이어그램

```
탭 0: 주식 설정
    │
    ├─ data_ready
    │  └──> MainWindow::on_data_loaded
    │       └──> 탭 1 활성화
    │       └──> DataLoadedSignal 발송
    │
    └─ error_occurred
       └──> MainWindow::show_error_dialog

탭 1: 전략 선택
    │
    ├─ strategy_changed
    │  └──> MainWindow::update_parameter_widgets
    │
    ├─ parameters_validated
    │  └──> MainWindow::on_params_validated
    │       └──> 탭 2 활성화
    │       └──> 탭 3 활성화/비활성화
    │
    └─ error_occurred
       └──> MainWindow::show_error_dialog

탭 2: 최적화
    │
    ├─ optimization_started
    │  └──> MainWindow::start_optimization_worker
    │
    ├─ optimization_progress
    │  └──> MainWindow::update_progress_bar
    │
    ├─ optimization_complete
    │  └──> MainWindow::on_optimization_complete
    │       └──> 결과 탭 업데이트
    │       └──> 탭 3 활성화
    │
    └─ error_occurred
       └──> MainWindow::show_error_dialog

워커 스레드
    │
    ├─ DataDownloadWorker
    │  ├─ download_progress → progress_bar.setValue()
    │  ├─ download_complete → MainWindow::on_data_downloaded()
    │  └─ error_signal → MainWindow::show_error_dialog()
    │
    ├─ BacktestWorker
    │  ├─ backtest_progress → progress_bar.setValue()
    │  ├─ backtest_complete → MainWindow::on_backtest_complete()
    │  └─ error_signal → MainWindow::show_error_dialog()
    │
    └─ OptimizationWorker
       ├─ optimization_progress → progress_bar.setValue()
       ├─ found_better_params → results_tab.update_best_so_far()
       ├─ optimization_complete → MainWindow::on_optimization_complete()
       └─ error_signal → MainWindow::show_error_dialog()
```

---

## 스레딩 통합

### 워커 스레드 패턴

데이터 다운로드, 백테스트, 최적화는 모두 별도의 워커 스레드에서 실행되어 UI가 반응성을 유지합니다.

**주요 특징**:
- 비차단(Non-blocking) 작업
- 실시간 진행률 업데이트
- 취소 가능
- 에러 처리
- 완료 신호

---

## 데이터 흐름

### 완전한 상호작용 시퀀스

**사용자 액션: 주식 선택 & 데이터 다운로드**

```
사용자 액션 → 입력 검증 → 데이터 다운로드 워커 시작
              ↓
        캐시 확인 → 캐시 히트: SQLite에서 로드
              → 캐시 미스: Yahoo Finance 다운로드
              ↓
        데이터프레임 반환 → data_ready 신호 발송
              ↓
        MainWindow::on_data_loaded()
        ├─ ApplicationState 업데이트
        ├─ 탭 1 활성화
        ├─ 탭 1로 전환
        ├─ dataLoadedSignal 발송
        └─ 상태 표시줄 업데이트
```

---

## 에러 처리

### 에러 처리 전략

**입력 검증**:
- 티커: 1-5자 영숫자만
- 날짜: 시작 < 종료
- 파라미터: 최소/최대 범위 확인

**에러 메시지**:
- 사용자 친화적 메시지
- 기술적 세부사항 로그
- 재시도 옵션 제공

---

## 스타일링 & 테마

### 다크 테마 (기본)

**색상**:
- 주요: #0D47A1 (진한 파란색)
- 배경: #1E1E1E (매우 진한 회색)
- 표면: #2D2D2D (진한 회색)
- 테두리: #3D3D3D (회색)
- 텍스트: #FFFFFF (흰색)

**의미론적 색상**:
- 성공: #4CAF50 (녹색)
- 경고: #FF9800 (주황색)
- 에러: #F44336 (빨간색)
- 정보: #2196F3 (하늘색)

---

## 상호작용 흐름

### 흐름 1: 기본 백테스트

```
탭 0: 주식 설정
    ↓ [데이터 다운로드]
    ↓ (1-30초 다운로드)
탭 1: 전략 선택 (활성화)
    ↓ [전략 & 파라미터 선택]
    ↓ [검증]
탭 2: 최적화 (활성화)
    ↓ [최적화 스킵]
    ↓ [백테스트 실행]
    ↓ (1-2초 백테스트)
탭 3: 결과 (자동 전환)
    ↓ [지표 & 차트 표시]
    ↓ [필요시 내보내기]
```

**소요 시간**: 5-10분 (대부분 다운로드 시간)

### 흐름 2: 완전 최적화

```
탭 2: 최적화 (활성화)
    ↓ [파라미터 범위 설정]
    ↓ [520개 조합 계산]
    ↓ [최적화 시작]
    ↓ (10-30분 진행 중)
    ├─ 실시간: "235/520 - 최선: 467%"
    ├─ 진행률: 47%
    └─ 차트 실시간 업데이트
    ↓ [완료]
탭 3: 결과 (자동 전환)
    ↓ [최적 파라미터 표시]
    ↓ [최선 지표 표시]
```

**소요 시간**: 15-45분 (범위에 따라 다름)

---

**GUI 아키텍처 문서 끝**

이 문서는 QuantInvest Tool의 PySide6 기반 사용자 인터페이스의 완전한 설계 및 구현 가이드를 제공합니다.
