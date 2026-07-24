# QuantInvest Tool - 시스템 아키텍처

## 시스템 개요

QuantInvest Tool은 Jupyter 노트북으로 작성된 정량적(퀀트) 트레이딩 전략을 대화형 GUI 도구로 변환하는 모듈형 애플리케이션입니다. 이 시스템은 데이터, 비즈니스 로직, 프레젠테이션 계층 간의 관심사를 분리한 클린 아키텍처를 따릅니다.

### 핵심 설계 원칙
1. **모듈성(Modularity)**: 각 전략과 구성 요소가 독립적으로 동작합니다
2. **테스트 가능성(Testability)**: 비즈니스 로직이 UI와 분리되어 있습니다
3. **성능(Performance)**: 캐싱을 통해 중복 API 호출을 최소화합니다
4. **확장성(Extensibility)**: 새로운 전략과 기능을 손쉽게 추가할 수 있습니다
5. **사용자 친화성(User-Friendly)**: 명확한 워크플로를 갖춘 반응형 GUI를 제공합니다

---

## 아키텍처 계층

```
┌─────────────────────────────────────────────────────────────┐
│                   PySide6 User Interface                     │
│  (Main Window, Dialogs, Charts, Configuration Forms)        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              Application Logic Layer                          │
│  (UI Controllers, Event Handlers, State Management)          │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┬──────────────┐
        │                  │                  │              │
┌───────▼────┐  ┌──────────▼──────┐  ┌──────▼──────┐  ┌────▼──────┐
│ Strategy   │  │   Backtesting   │  │    Data     │  │  Metrics  │
│   Layer    │  │    Engine       │  │    Layer    │  │ Calc      │
│            │  │                 │  │             │  │           │
│ • Momentum │  │ • Event Loop    │  │ • Cache Mgr │  │ • CAGR    │
│ • Trend    │  │ • Position Mgmt │  │ • Downloader│  │ • Sharpe  │
│ • Mean Rev │  │ • Trade Tracking│  │ • SQLite    │  │ • MDD     │
│ • Portfolio│  │ • Signals       │  │             │  │ • Win Rate│
└────────────┘  └─────────────────┘  └─────────────┘  └───────────┘
        │                                      │
        └──────────────────┬───────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                External Services                             │
│  (yfinance API, SQLite Database, Matplotlib)                │
└──────────────────────────────────────────────────────────────┘
```

---

## 데이터 흐름 아키텍처

### 1. 전체 사용자 워크플로

```
START
  │
  ├─→ User Opens Application
  │   └─→ UI Loads Default Configuration
  │       └─→ Cache Status: Ready
  │
  ├─→ User Selects Stock & Date Range
  │   ├─→ Download Data (or Use Cache)
  │   │   ├─→ Check SQLite Cache
  │   │   ├─→ If Missing: yfinance Download
  │   │   └─→ Store in Cache
  │   └─→ Data Loaded in Memory
  │
  ├─→ User Selects Strategy & Parameters
  │   ├─→ Momentum: momentum_period, mfi_level, stop_loss
  │   ├─→ Trend Following: short_window, long_window, stop_loss
  │   ├─→ Mean Reversion: z_score, lookback, position_size
  │   └─→ Portfolio: portfolio_size, weight_method
  │
  ├─→ [Optional] User Enables Parameter Optimization
  │   ├─→ Define Parameter Ranges
  │   ├─→ Grid Search Algorithm Starts
  │   │   ├─→ Iterate through all combinations
  │   │   ├─→ Run backtest for each
  │   │   ├─→ Track best parameters
  │   │   └─→ Show Progress Bar
  │   └─→ Return Optimal Parameters
  │
  ├─→ Run Backtest
  │   ├─→ Initialize Portfolio (cash = $10,000)
  │   ├─→ For Each Trading Day:
  │   │   ├─→ Calculate Technical Indicators
  │   │   ├─→ Generate Buy/Sell Signals
  │   │   ├─→ Execute Trades (if signal)
  │   │   ├─→ Update Position & Cash
  │   │   ├─→ Record Portfolio Value
  │   │   └─→ Check Stop Losses
  │   └─→ Backtest Complete
  │
  ├─→ Calculate Performance Metrics
  │   ├─→ CAGR (Compound Annual Growth Rate)
  │   ├─→ Sharpe Ratio (Risk-Adjusted Return)
  │   ├─→ Maximum Drawdown
  │   ├─→ Win Rate (% Profitable Trades)
  │   └─→ Profit/Loss Ratio
  │
  ├─→ Visualize Results
  │   ├─→ Plot 1: Cumulative Returns (Strategy vs Buy&Hold)
  │   ├─→ Plot 2: Technical Indicators (Price + MA/EMA/etc)
  │   ├─→ Plot 3: Buy/Sell Signals on Price Chart
  │   ├─→ Plot 4: Drawdown Over Time
  │   └─→ Display in Tabs
  │
  ├─→ [Optional] Export Results
  │   ├─→ Save to CSV/Excel
  │   ├─→ Export Charts as PNG
  │   └─→ Generate Report PDF
  │
  └─→ END

```

### 2. 상세 백테스트 루프

```
BACKTEST(strategy, data, parameters)
│
├─ Initialize State:
│   ├─ cash = initial_capital (default: $10,000)
│   ├─ position = 0 (no holdings)
│   ├─ entry_price = None
│   ├─ stop_loss_price = None
│   ├─ portfolio_values = []
│   ├─ buy_signals = []
│   ├─ sell_signals = []
│   └─ trade_history = []
│
├─ For i = 0 to len(data):
│   │
│   ├─ Fetch Current Bar Data:
│   │   ├─ price = data['Close'][i]
│   │   ├─ signal = data['Signal'][i]
│   │   └─ indicators = [MA, EMA, MFI, RSI, etc]
│   │
│   ├─ Position State Machine:
│   │   │
│   │   ├─ IF position == 0 (No Position):
│   │   │   │
│   │   │   └─ IF signal == BUY:
│   │   │       ├─ Sufficient Cash?
│   │   │       │   └─ YES: Execute Buy
│   │   │       │       ├─ shares = cash / (price × (1 + fee))
│   │   │       │       ├─ cash = cash - (price × shares × (1+fee))
│   │   │       │       ├─ entry_price = price
│   │   │       │       ├─ stop_loss_price = price × (1 - stop_loss%)
│   │   │       │       ├─ position = 1
│   │   │       │       └─ record BUY signal
│   │   │       └─ NO: Skip (insufficient capital)
│   │   │
│   │   ├─ ELIF position == 1 (Holding Position):
│   │   │   │
│   │   │   ├─ Check Stop Loss:
│   │   │   │   └─ IF price < stop_loss_price:
│   │   │   │       ├─ Execute Sell
│   │   │   │       ├─ cash = cash + (price × shares × (1-fee))
│   │   │   │       ├─ position = 0
│   │   │   │       ├─ record SELL signal
│   │   │   │       └─ record Trade Loss
│   │   │   │
│   │   │   ├─ Update Trailing Stop Loss:
│   │   │   │   └─ IF price > entry_price:
│   │   │   │       └─ stop_loss_price = MAX(stop_loss_price, 
│   │   │   │                                 price × (1 - stop_loss%))
│   │   │   │
│   │   │   └─ Check Exit Signal:
│   │   │       └─ IF signal == SELL:
│   │   │           ├─ Execute Sell
│   │   │           ├─ cash = cash + (price × shares × (1-fee))
│   │   │           ├─ position = 0
│   │   │           ├─ record SELL signal
│   │   │           └─ record Trade Profit
│   │
│   ├─ Update Portfolio Value:
│   │   └─ IF position == 0:
│   │       └─ portfolio_value[i] = cash
│   │       ELSE:
│   │       └─ portfolio_value[i] = cash + (shares × price)
│   │
│   └─ Record State for Visualization
│
├─ Calculate Returns:
│   ├─ cumulative_return = portfolio_value / initial_capital
│   ├─ daily_returns = price_change / previous_price
│   └─ cumulative_max = running maximum of cumulative_return
│
└─ RETURN backtest_results

```

### 3. 파라미터 최적화 루프

```
OPTIMIZE_PARAMETERS(strategy, data, param_ranges)
│
├─ Define Parameter Grid:
│   ├─ param1_range = [1, 2, 3, ..., 20]  (e.g., period)
│   ├─ param2_range = [5, 10, 15, ..., 50] (e.g., window)
│   └─ param3_range = [0.02, 0.05, 0.1, ..., 0.2] (e.g., stop_loss)
│
├─ Initialize Tracking:
│   ├─ results = []  # [(param1, param2, param3, return), ...]
│   └─ best_return = -∞
│
├─ For each param1 in param1_range:
│   │
│   └─ For each param2 in param2_range:
│       │
│       └─ For each param3 in param3_range:
│           │
│           ├─ Run Backtest(strategy, data, [param1, param2, param3])
│           ├─ final_return = cumulative_return[-1]
│           ├─ results.append((param1, param2, param3, final_return))
│           │
│           ├─ IF final_return > best_return:
│           │   └─ best_return = final_return
│           │       best_params = [param1, param2, param3]
│           │
│           └─ Update Progress Bar
│
├─ Post-Processing:
│   ├─ Find all params with return == best_return
│   ├─ Take median of each param (for robustness)
│   └─ optimal_params = median across ties
│
└─ RETURN optimal_params, results_dataframe

```

---

## 구성 요소 상호작용 다이어그램

### 전략 실행 흐름

```
┌────────────────┐
│   UI Handler   │  User clicks "Run Backtest"
└────────┬───────┘
         │
         ▼
┌────────────────────────────┐
│ Strategy Factory           │
│ - Creates strategy object  │
│ - Sets user parameters     │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Data Layer                 │
│ - Check SQLite cache       │
│ - Download if needed       │
│ - Return DataFrame         │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Strategy.calculate_signals │
│ - Compute indicators       │
│ - Generate buy/sell marks  │
│ - Return signals           │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Backtest Engine            │
│ - Run event loop           │
│ - Track portfolio          │
│ - Process trades           │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Metrics Calculator         │
│ - Compute CAGR, Sharpe     │
│ - Max Drawdown, Win Rate   │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│ Plotting Engine            │
│ - Create matplotlib figs   │
│ - Embed in Qt dialogs      │
│ - Display results          │
└────────────────────────────┘

```

### 단일 거래의 데이터 흐름

```
Price Stream: 100 → 101 → 102 → 99 → 98 → 97 → 96
                   ↓
              BUY Signal
                   ↓
        ┌─ BUY @ 101
        │   ├─ shares = 10000 / 101 / 1.001 ≈ 98.9 shares
        │   ├─ cash = 10000 - 10000 = $0
        │   ├─ entry_price = 101
        │   └─ stop_loss = 101 × (1 - 0.05) = 95.95
        │
        ├─ Update Stop Loss @ 102
        │   └─ trailing_stop = 102 × (1 - 0.05) = 96.9
        │
        ├─ Price Falls: 99, 98, 97
        │   └─ Position held (no stop loss yet)
        │
        └─ STOP LOSS TRIGGERED @ 96
            ├─ SELL @ 96
            ├─ cash = 0 + (96 × 98.9 × 0.999) = 9504.38
            ├─ Profit = (9504.38 / 10000) - 1 = -4.96%
            └─ Position = 0

```

### 캐시 관리

```
User Requests: AAPL, 2023-01-01 to 2024-01-01
       │
       ▼
┌──────────────────────────┐
│ Cache.check_availability │
│ (SQLite query)           │
└────┬─────────────────────┘
     │
     ├─ CASE 1: Complete data in cache
     │   └─→ Load from disk (fast: <1s)
     │
     ├─ CASE 2: Partial cache
     │   ├─→ Load cached portion
     │   ├─→ Download missing dates
     │   ├─→ Combine & store updated cache
     │   └─→ Return complete data
     │
     └─ CASE 3: No cache
         ├─→ Download from yfinance
         ├─→ Store in SQLite
         └─→ Return data

Typical Cache Hit Rate: 70-80% for repeated stocks

```

---

## 기술 스택 세부 사항

### PySide6 아키텍처
```
QApplication (event loop)
    │
    ├─ MainWindow
    │   ├─ QTabWidget
    │   │   ├─ Tab 1: Stock Configuration
    │   │   │   ├─ QLineEdit (ticker)
    │   │   │   ├─ QDateEdit (start/end)
    │   │   │   └─ QPushButton (fetch data)
    │   │   │
    │   │   ├─ Tab 2: Strategy Selection
    │   │   │   ├─ QComboBox (strategy type)
    │   │   │   ├─ QLineEdit (parameters)
    │   │   │   └─ QPushButton (validate)
    │   │   │
    │   │   ├─ Tab 3: Optimization
    │   │   │   ├─ QCheckBox (enable)
    │   │   │   ├─ QSpinBox (param ranges)
    │   │   │   └─ QProgressBar
    │   │   │
    │   │   └─ Tab 4: Results
    │   │       ├─ QTableWidget (metrics)
    │   │       ├─ FigureCanvas (plots)
    │   │       └─ QPushButton (export)
    │   │
    │   ├─ QStatusBar (status messages)
    │   └─ QMenuBar (File, Help)
    │
    ├─ Worker Threads
    │   ├─ DataDownloadThread
    │   ├─ BacktestThread
    │   └─ OptimizationThread
    │
    └─ Dialogs
        ├─ DateRangeDialog
        ├─ ParameterDialog
        ├─ ChartDialog
        └─ ProgressDialog
```

### 데이터베이스 스키마

```sql
-- SQLite Tables

CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    date DATE NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL NOT NULL,
    volume INTEGER,
    UNIQUE(ticker, date)
);

CREATE INDEX idx_ticker_date ON price_history(ticker, date);

-- Query Example:
SELECT * FROM price_history 
WHERE ticker = 'AAPL' 
  AND date BETWEEN '2023-01-01' AND '2024-01-01'
ORDER BY date;
```

---

## 스레딩 모델

```
Main Thread (UI)
    │
    ├─ QMainWindow (always responsive)
    │
    ├─ Emit Signal → DataDownloadWorker
    │   │
    │   └─ Worker Thread 1
    │       ├─ yfinance.download()
    │       ├─ SQLite INSERT
    │       └─ Emit finished_signal(data)
    │
    ├─ Emit Signal → BacktestWorker
    │   │
    │   └─ Worker Thread 2
    │       ├─ Backtest loop
    │       ├─ Metrics calculation
    │       └─ Emit results_signal(metrics, data)
    │
    └─ Emit Signal → OptimizationWorker
        │
        └─ Worker Thread 3 (Optional: Multiprocessing Pool)
            ├─ Grid search loop
            ├─ Parallel backtests
            └─ Emit optimization_signal(best_params)

Signals → Slots Pattern:
  download_complete → update_ui()
  backtest_complete → display_results()
  optimization_complete → show_optimal_params()
```

---

## 성능 특성

### 일반적인 실행 시간
```
Data Download (new):     5-30 seconds  (network dependent)
Data Fetch (cached):     <1 second
Single Backtest:         0.5-2 seconds
Parameter Optimization:  2-60 minutes  (depends on param ranges)
Metrics Calculation:     <1 second
Plotting:               1-3 seconds
Export to CSV:          <1 second
```

### 메모리 사용량
```
5 years of daily data:   ~1-2 MB per stock
Backtest state:          ~10 MB
Optimization (in-memory):~100-500 MB (depends on cache)
```

---

## 보안 고려 사항

1. **데이터 처리(Data Handling)**: 공개된 주식 데이터만 다운로드합니다
2. **로컬 캐시(Local Cache)**: SQLite가 데이터를 로컬에 저장합니다(클라우드 동기화 없음)
3. **입력 검증(Input Validation)**: 모든 사용자 입력을 사용 전에 검증합니다
4. **자격 증명 없음(No Credentials)**: 사용자 인증이나 비밀 정보를 저장하지 않습니다
5. **샌드박스 실행(Sandboxed Execution)**: 시스템 호출이나 외부 프로세스를 사용하지 않습니다

---

## 확장 지점

### 새로운 전략 추가
```python
class CustomStrategy(BaseStrategy):
    def calculate_signals(self, data):
        # 사용자 정의 지표 로직
        pass
    
    def run_backtest(self, data):
        # 사용자 정의 백테스트 루프
        pass
```

### 사용자 정의 지표 추가
```python
def calculate_custom_metric(returns, benchmark):
    # 지표 계산
    return metric_value
```

### 새로운 시각화 추가
```python
def plot_custom_analysis(backtest_data):
    fig, ax = plt.subplots()
    # 플로팅 로직
    return fig
```

---

**Last Updated**: 2026-07-24
**Version**: 1.0
