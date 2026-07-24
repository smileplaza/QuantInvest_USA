# QuantInvest Tool - Detailed GUI Architecture

## Table of Contents
1. [Overview](#overview)
2. [Widget Hierarchy](#widget-hierarchy)
3. [Tab-by-Tab Design](#tab-by-tab-design)
4. [State Management](#state-management)
5. [Signal/Slot Architecture](#signalslot-architecture)
6. [Threading Integration](#threading-integration)
7. [Data Flow](#data-flow)
8. [Error Handling](#error-handling)
9. [Styling & Themes](#styling--themes)
10. [Interaction Flows](#interaction-flows)

---

## Overview

The QuantInvest Tool GUI is built with **PySide6** using a tabbed interface with clear separation between data input, strategy configuration, optimization settings, and results analysis. The architecture emphasizes responsiveness through worker threads and real-time feedback.

### Design Philosophy
- **Modular**: Each tab is self-contained but shares application state
- **Responsive**: Long operations run in background threads
- **Clear Feedback**: Real-time progress, error messages, and status updates
- **Professional**: Clean, organized interface with intuitive workflow

---

## Widget Hierarchy

### Application Widget Tree

```
QApplication
    │
    └─ QMainWindow (MainWindow)
        │
        ├─ QMenuBar
        │   ├─ File Menu
        │   │   ├─ New Session
        │   │   ├─ Load Session
        │   │   ├─ Save Session
        │   │   ├─ Export Results
        │   │   └─ Exit
        │   └─ Help Menu
        │       ├─ About
        │       ├─ Documentation
        │       └─ Settings
        │
        ├─ QToolBar (Optional: Quick Access)
        │   ├─ Quick Run Button
        │   ├─ Stop Button
        │   └─ Clear Cache Button
        │
        ├─ QWidget (Central Widget)
        │   │
        │   ├─ QVBoxLayout
        │   │   │
        │   │   ├─ QTabWidget (Tab Container)
        │   │   │   │
        │   │   │   ├─ Tab 0: Stock Configuration
        │   │   │   │   └─ StockConfigWidget
        │   │   │   │
        │   │   │   ├─ Tab 1: Strategy Selection
        │   │   │   │   └─ StrategySelectionWidget
        │   │   │   │
        │   │   │   ├─ Tab 2: Optimization Settings
        │   │   │   │   └─ OptimizationWidget
        │   │   │   │
        │   │   │   └─ Tab 3: Results & Analysis
        │   │   │       └─ ResultsAnalysisWidget
        │   │   │
        │   │   └─ QFrame (Status/Control Bar)
        │   │       ├─ QProgressBar
        │   │       ├─ QLabel (Status Message)
        │   │       └─ QPushButton (Cancel)
        │   │
        │   └─ QStatusBar
        │       ├─ QLabel (Left: Session Name)
        │       ├─ QLabel (Center: Operation Status)
        │       └─ QLabel (Right: Data Cache Status)
        │
        └─ Worker Threads (Background)
            ├─ DataDownloadWorker
            ├─ BacktestWorker
            └─ OptimizationWorker

```

### Class Structure

```python
# Main Application Classes

QMainWindow
    └─ MainWindow
        ├─ manages all tabs
        ├─ handles inter-tab communication
        ├─ creates worker threads
        └─ coordinates application state

QWidget
    ├─ StockConfigWidget
    │   ├─ stock input fields
    │   ├─ date range selectors
    │   └─ fetch data button
    │
    ├─ StrategySelectionWidget
    │   ├─ strategy dropdown
    │   ├─ dynamic parameter inputs
    │   └─ validation logic
    │
    ├─ OptimizationWidget
    │   ├─ enable/disable checkbox
    │   ├─ parameter range inputs
    │   └─ optimization controls
    │
    └─ ResultsAnalysisWidget
        ├─ metrics table
        ├─ chart display area
        └─ export buttons

QThread (Worker)
    ├─ DataDownloadWorker
    ├─ BacktestWorker
    └─ OptimizationWorker
```

---

## Tab-by-Tab Design

### Tab 0: Stock Configuration

**Purpose**: Download and prepare stock data

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│ Stock & Date Configuration                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Stock Selection:                                    │
│  ┌────────────────────────────────────────────┐   │
│  │ Stock Ticker (e.g., AAPL, MSFT, TSLA)     │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
│ Date Range:                                         │
│  ┌──────────────────┐  ┌──────────────────┐      │
│  │ Start Date       │  │ End Date         │      │
│  │ [2023-01-01] ▼  │  │ [2024-01-01] ▼   │      │
│  └──────────────────┘  └──────────────────┘      │
│                                                     │
│  ☑ Use Cached Data (if available)                 │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │         [Fetch Data from yfinance]         │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
│ Data Preview:                                       │
│  ┌────────────────────────────────────────────┐   │
│  │ Ticker: AAPL                               │   │
│  │ Date Range: 2023-01-01 to 2024-01-01      │   │
│  │ Days: 252 trading days                     │   │
│  │ Loaded: 4,500 rows of OHLCV data          │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Components**:
```python
class StockConfigWidget(QWidget):
    # Inputs
    stock_input = QLineEdit()           # Ticker symbol
    start_date = QDateEdit()            # Start date
    end_date = QDateEdit()              # End date
    use_cache_checkbox = QCheckBox()    # Use cached data
    
    # Buttons
    fetch_button = QPushButton("Fetch Data")
    clear_cache_button = QPushButton("Clear Cache")
    
    # Display
    preview_label = QLabel()            # Data preview
    status_label = QLabel()             # Status message
    progress_bar = QProgressBar()       # Download progress
    
    # Signals
    data_ready = Signal(pd.DataFrame)
    download_started = Signal()
    error_occurred = Signal(str)
```

**Workflows**:
1. User enters ticker symbol
2. User selects date range
3. Click "Fetch Data"
   - Check cache for data
   - If cache hit: Load from SQLite
   - If cache miss: Download from yfinance
   - Display preview
   - Emit signal to enable next tab

**Validation**:
- Ticker length: 1-5 characters
- Date range: end_date > start_date
- Date range: Not more than 30 years
- Ticker format: Alphanumeric only

---

### Tab 1: Strategy Selection & Parameters

**Purpose**: Configure trading strategy and parameters

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│ Strategy Selection & Parameters                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Select Strategy:                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │ Strategy: [Momentum ▼]                       │  │
│  │ Description: Trades on price momentum...     │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│ Strategy Parameters:                                │
│  ┌──────────────────────────────────────────────┐  │
│  │ Momentum Period: [12         ] (3-30)        │  │
│  │ MFI Level:       [46.5   ▬▬▬▬▬▬▬▬] (20-80) │  │
│  │ Stop Loss:       [7%         ] (1%-20%)      │  │
│  │                                              │  │
│  │ ⓘ Momentum Period: Number of days for mom   │  │
│  │ ⓘ MFI Level: Money Flow Index threshold     │  │
│  │ ⓘ Stop Loss: Maximum loss before exit       │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ☑ Use Defaults  ☑ Advanced Settings               │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │   [Reset to Defaults] [Validate Parameters]  │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│ Parameter Presets:  [Save as Preset] [Load Preset] │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Components**:
```python
class StrategySelectionWidget(QWidget):
    # Strategy selection
    strategy_combo = QComboBox()        # Momentum, TrendFollowing, MeanReversion, Portfolio
    description_label = QLabel()        # Strategy description
    
    # Dynamic parameter inputs
    parameter_widgets = []              # List of parameter input widgets
    parameter_layout = QFormLayout()    # Grid for parameter inputs
    
    # Buttons
    validate_button = QPushButton("Validate Parameters")
    reset_button = QPushButton("Reset to Defaults")
    
    # Presets
    preset_combo = QComboBox()          # Load saved presets
    save_preset_button = QPushButton("Save as Preset")
    
    # Signals
    strategy_changed = Signal(str)
    parameters_validated = Signal(dict)
    error_occurred = Signal(str)
```

**Strategy Parameter Definitions**:

```python
STRATEGY_PARAMS = {
    "Momentum": {
        "momentum_period": {"type": "int", "min": 3, "max": 30, "default": 12},
        "mfi_level": {"type": "float", "min": 20, "max": 80, "default": 46.5},
        "stop_loss": {"type": "float", "min": 0.01, "max": 0.20, "default": 0.07}
    },
    "TrendFollowing": {
        "short_window": {"type": "int", "min": 5, "max": 30, "default": 12},
        "long_window": {"type": "int", "min": 20, "max": 100, "default": 26},
        "stop_loss": {"type": "float", "min": 0.01, "max": 0.20, "default": 0.07}
    },
    "MeanReversion": {
        "lookback_period": {"type": "int", "min": 5, "max": 50, "default": 20},
        "z_score": {"type": "float", "min": 0.5, "max": 3.0, "default": 1.96},
        "position_size": {"type": "float", "min": 0.01, "max": 1.0, "default": 0.5}
    },
    "Portfolio": {
        "portfolio_size": {"type": "int", "min": 2, "max": 10, "default": 5},
        "correlation_filter": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.7},
        "weight_method": {"type": "choice", "options": ["equal", "market_cap", "inverse_variance"], "default": "equal"}
    }
}
```

**Workflow**:
1. User selects strategy from dropdown
2. Description and parameters display dynamically
3. User adjusts parameters or uses defaults
4. Click "Validate Parameters"
5. Validation checks min/max constraints
6. If valid: Enable next tab
7. If invalid: Show error message

---

### Tab 2: Optimization Settings

**Purpose**: Configure parameter search ranges

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│ Parameter Optimization Settings                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ☐ Enable Parameter Optimization                    │
│                                                     │
│ Parameter Search Ranges:                            │
│ ┌──────────────────────────────────────────────┐   │
│ │ Momentum Period:   [3  ...  30] step 1        │   │
│ │ MFI Level:         [20 ...  80] step 5        │   │
│ │ Stop Loss:         [1% ... 20%] step 1%       │   │
│ │                                              │   │
│ │ Estimated Combinations: 28 × 13 × 20 = 7,280   │   │
│ │ Estimated Time: ~10-15 minutes                   │   │
│ └──────────────────────────────────────────────┘   │
│                                                     │
│ Optimization Options:                               │
│  ☑ Parallel Processing  [Threads: 4  ▼]           │
│  ☑ Show Progress        ☑ Auto-select Best        │
│                                                     │
│ Constraints:                                        │
│  ☐ Minimum Annual Return:    [0%]                 │
│  ☐ Maximum Drawdown:         [50%]                │
│  ☐ Minimum Win Rate:         [0%]                 │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │   [Reset Ranges] [Start Optimization]      │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Components**:
```python
class OptimizationWidget(QWidget):
    # Enable/disable
    enable_checkbox = QCheckBox("Enable Parameter Optimization")
    
    # Parameter ranges
    range_widgets = []                  # List of range input pairs
    range_layout = QFormLayout()        # Grid for range inputs
    
    # Display
    combination_label = QLabel()        # Number of combinations
    time_estimate_label = QLabel()      # Time estimate
    
    # Options
    parallel_checkbox = QCheckBox("Parallel Processing")
    thread_spinbox = QSpinBox()         # Number of threads
    progress_checkbox = QCheckBox("Show Progress")
    auto_select_checkbox = QCheckBox("Auto-select Best")
    
    # Constraints
    min_return_spinbox = QDoubleSpinBox()
    max_drawdown_spinbox = QDoubleSpinBox()
    min_win_rate_spinbox = QDoubleSpinBox()
    
    # Buttons
    reset_button = QPushButton("Reset Ranges")
    start_button = QPushButton("Start Optimization")
    
    # Signals
    optimization_started = Signal(dict)
    optimization_progress = Signal(int, int)  # current, total
    optimization_complete = Signal(dict)
    error_occurred = Signal(str)
```

**Workflow**:
1. User enables optimization checkbox
2. Parameter ranges auto-populate from strategy defaults
3. User adjusts ranges
4. System calculates combinations and time estimate
5. User sets optional constraints
6. Click "Start Optimization"
7. Optimization runs in background (progress updates in real-time)
8. Results display in Tab 3

---

### Tab 3: Results & Analysis

**Purpose**: Display backtesting results and analysis

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│ Results & Analysis                                  │
├───────────────┬─────────────────────────────────────┤
│ Metrics Table │ Chart Tabs                          │
├───────────────┼─────────────────────────────────────┤
│               │ [Cumulative Returns] [Indicators]   │
│ CAGR      38% │ [Buy/Sell Signals]  [Drawdown]     │
│ Sharpe    1.46│                                     │
│ MDD      -33% │ ┌─────────────────────────────────┐│
│ Win Rate  50% │ │                                 ││
│ P/L Ratio 4.9 │ │    Cumulative Returns Chart     ││
│               │ │                                 ││
│ Trades       │ │    ┌───────────────────────────┐ ││
│ Buy  10       │ │    │ 5x ─────────────────────┐ │ ││
│ Sell 10       │ │    │    │        ┌────────── │ │ ││
│ Profit  10    │ │    │ 2x ┤────────┤          │ │ ││
│ Loss    0     │ │    │    │        └──────────┤ │ ││
│               │ │    │ 1x ├────────────────────┤ │ ││
│ [Copy Metrics]│ │    │    │◆ Buy  ▼ Sell      │ │ ││
│               │ │    └────┴──────────────────────┘ ││
│               │ │    2023-01         2024-01       ││
│               │ └─────────────────────────────────┘│
│               │                                     │
│               │ [Export CSV] [Export Charts]        │
│               │ [Generate PDF Report]               │
│               │                                     │
└───────────────┴─────────────────────────────────────┘
```

**Components**:
```python
class ResultsAnalysisWidget(QWidget):
    # Metrics table
    metrics_table = QTableWidget()      # Scrollable metrics
    copy_metrics_button = QPushButton("Copy Metrics")
    
    # Chart tabs
    chart_tabs = QTabWidget()           # Chart type selector
    
    # Chart types
    cumulative_returns_canvas = MatplotlibCanvas()
    indicators_canvas = MatplotlibCanvas()
    buy_sell_canvas = MatplotlibCanvas()
    drawdown_canvas = MatplotlibCanvas()
    
    # Export buttons
    export_csv_button = QPushButton("Export CSV")
    export_charts_button = QPushButton("Export Charts")
    export_pdf_button = QPushButton("Generate PDF Report")
    
    # Signals
    export_requested = Signal(str)  # Export type
```

**Display Structure**:
```python
# Metrics table data
metrics_data = [
    ("Strategy", "Momentum"),
    ("Stock", "AAPL"),
    ("Period", "2023-01-01 to 2024-01-01"),
    ("", ""),  # Spacer
    ("CAGR", "38.37%"),
    ("Sharpe Ratio", "1.46"),
    ("Max Drawdown", "-32.87%"),
    ("Win Rate", "50.00%"),
    ("Profit/Loss Ratio", "4.92"),
    ("", ""),  # Spacer
    ("Total Trades", "20"),
    ("Winning Trades", "10"),
    ("Losing Trades", "10"),
    ("Avg Profit", "24.9%"),
    ("Avg Loss", "-5.1%"),
    ("Avg Holding Period", "47.5 days"),
]
```

---

## State Management

### Application State Model

```python
class ApplicationState:
    """Central state management for all tabs"""
    
    # Stock data
    stock_ticker: str = None
    start_date: QDate = None
    end_date: QDate = None
    stock_data: pd.DataFrame = None
    
    # Strategy configuration
    strategy_name: str = "Momentum"
    strategy_params: Dict[str, float] = {}
    
    # Optimization settings
    optimization_enabled: bool = False
    optimization_params: Dict[str, Tuple[float, float]] = {}
    optimization_constraints: Dict[str, float] = {}
    
    # Results
    backtest_results: Dict = None
    performance_metrics: Dict = None
    optimal_params: Dict = None
    
    # UI state
    current_tab: int = 0
    last_operation: str = None
    error_message: str = None
    
    # Methods
    def update_stock_data(self, ticker, start, end, data):
        self.stock_ticker = ticker
        self.start_date = start
        self.end_date = end
        self.stock_data = data
    
    def update_strategy(self, name, params):
        self.strategy_name = name
        self.strategy_params = params
    
    def set_results(self, results):
        self.backtest_results = results
        self.performance_metrics = results.metrics
```

### State Sharing Between Tabs

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create shared state
        self.state = ApplicationState()
        
        # Create tabs
        self.stock_config_tab = StockConfigWidget(self.state)
        self.strategy_tab = StrategySelectionWidget(self.state)
        self.optimization_tab = OptimizationWidget(self.state)
        self.results_tab = ResultsAnalysisWidget(self.state)
        
        # Connect state changes
        self.stock_config_tab.data_ready.connect(self.on_data_loaded)
        self.strategy_tab.parameters_validated.connect(self.on_params_validated)
        self.optimization_tab.optimization_complete.connect(self.on_optimization_complete)
        
        # Enable/disable tabs based on state
        self.update_tab_availability()
    
    def on_data_loaded(self, data):
        self.state.stock_data = data
        self.tabs.setTabEnabled(1, True)  # Enable strategy tab
        self.tabs.setCurrentIndex(1)      # Switch to strategy tab
    
    def update_tab_availability(self):
        """Enable/disable tabs based on completed steps"""
        self.tabs.setTabEnabled(1, self.state.stock_data is not None)
        self.tabs.setTabEnabled(2, self.state.strategy_params is not None)
        self.tabs.setTabEnabled(3, self.state.backtest_results is not None)
```

---

## Signal/Slot Architecture

### Signal Flow Diagram

```
Tab 0: Stock Config
    │
    ├─ data_ready
    │  └──> MainWindow::on_data_loaded
    │       └──> Enable Tab 1
    │       └──> Emit DataLoadedSignal
    │
    └─ error_occurred
       └──> MainWindow::show_error_dialog

Tab 1: Strategy Selection
    │
    ├─ strategy_changed
    │  └──> MainWindow::update_parameter_widgets
    │
    ├─ parameters_validated
    │  └──> MainWindow::on_params_validated
    │       └──> Enable Tab 2
    │       └──> Enable/Disable Tab 3
    │
    └─ error_occurred
       └──> MainWindow::show_error_dialog

Tab 2: Optimization
    │
    ├─ optimization_started
    │  └──> MainWindow::start_optimization_worker
    │
    ├─ optimization_progress
    │  └──> MainWindow::update_progress_bar
    │
    ├─ optimization_complete
    │  └──> MainWindow::on_optimization_complete
    │       └──> Update results tab
    │       └──> Enable Tab 3
    │
    └─ error_occurred
       └──> MainWindow::show_error_dialog

Worker Threads
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

### Signal Definitions

```python
# Main Window Signals
mainWindow.signals.data_loaded = Signal(pd.DataFrame)
mainWindow.signals.strategy_changed = Signal(str)
mainWindow.signals.parameters_validated = Signal(dict)
mainWindow.signals.backtest_started = Signal()
mainWindow.signals.backtest_complete = Signal(dict)
mainWindow.signals.optimization_progress = Signal(int, int)  # current, total
mainWindow.signals.optimization_complete = Signal(dict)
mainWindow.signals.error_occurred = Signal(str)
mainWindow.signals.operation_cancelled = Signal()

# Worker Signals
dataWorker.signals.progress = Signal(int)  # 0-100
dataWorker.signals.finished = Signal(pd.DataFrame)
dataWorker.signals.error = Signal(str)

backtestWorker.signals.progress = Signal(int)
backtestWorker.signals.finished = Signal(dict)  # results dict
backtestWorker.signals.error = Signal(str)

optimizationWorker.signals.progress = Signal(int, int)  # current, total
optimizationWorker.signals.found_better = Signal(dict)  # current best params
optimizationWorker.signals.finished = Signal(dict)  # final results
optimizationWorker.signals.error = Signal(str)
```

---

## Threading Integration

### Worker Thread Pattern

```python
class DataDownloadWorker(QRunnable):
    """Worker for downloading stock data"""
    
    class Signals(QObject):
        progress = Signal(int)          # 0-100
        finished = Signal(pd.DataFrame)
        error = Signal(str)
    
    def __init__(self, ticker, start_date, end_date, use_cache=True):
        super().__init__()
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.use_cache = use_cache
        self.signals = self.Signals()
    
    @Slot()
    def run(self):
        try:
            # Check cache first
            self.signals.progress.emit(10)
            data = cache_manager.get_data(self.ticker, self.start_date, self.end_date)
            
            if data is None:
                # Download from yfinance
                self.signals.progress.emit(30)
                data = yfinance.download(self.ticker, self.start_date, self.end_date)
                
                # Store in cache
                self.signals.progress.emit(70)
                cache_manager.store_data(self.ticker, data)
            
            self.signals.progress.emit(100)
            self.signals.finished.emit(data)
        except Exception as e:
            self.signals.error.emit(str(e))


class BacktestWorker(QRunnable):
    """Worker for running backtest"""
    
    class Signals(QObject):
        progress = Signal(int)
        finished = Signal(dict)  # results dict
        error = Signal(str)
    
    def __init__(self, strategy, data, parameters):
        super().__init__()
        self.strategy = strategy
        self.data = data
        self.parameters = parameters
        self.signals = self.Signals()
    
    @Slot()
    def run(self):
        try:
            self.signals.progress.emit(0)
            
            # Run backtest
            results = self.strategy.run_backtest(self.data, self.parameters)
            
            self.signals.progress.emit(50)
            
            # Calculate metrics
            metrics = calculate_metrics(results)
            
            self.signals.progress.emit(100)
            self.signals.finished.emit({
                'results': results,
                'metrics': metrics
            })
        except Exception as e:
            self.signals.error.emit(str(e))


class OptimizationWorker(QRunnable):
    """Worker for parameter optimization"""
    
    class Signals(QObject):
        progress = Signal(int, int)     # current, total
        found_better = Signal(dict)     # current best
        finished = Signal(dict)         # final results
        error = Signal(str)
    
    def __init__(self, strategy, data, param_ranges):
        super().__init__()
        self.strategy = strategy
        self.data = data
        self.param_ranges = param_ranges
        self.signals = self.Signals()
        self.best_result = None
        self.best_params = None
    
    @Slot()
    def run(self):
        try:
            # Generate parameter combinations
            combinations = generate_combinations(self.param_ranges)
            total = len(combinations)
            
            for i, params in enumerate(combinations):
                # Run backtest with these parameters
                results = self.strategy.run_backtest(self.data, params)
                metrics = calculate_metrics(results)
                return_value = metrics['cumulative_return']
                
                # Check if best so far
                if self.best_result is None or return_value > self.best_result:
                    self.best_result = return_value
                    self.best_params = params
                    self.signals.found_better.emit({
                        'params': params,
                        'return': return_value,
                        'metrics': metrics
                    })
                
                self.signals.progress.emit(i + 1, total)
            
            self.signals.finished.emit({
                'best_params': self.best_params,
                'best_return': self.best_result,
                'all_results': combinations  # Could optimize to not store all
            })
        except Exception as e:
            self.signals.error.emit(str(e))


# Usage in MainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool()
    
    def start_data_download(self, ticker, start_date, end_date):
        worker = DataDownloadWorker(ticker, start_date, end_date)
        worker.signals.progress.connect(self.update_progress)
        worker.signals.finished.connect(self.on_data_loaded)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)
    
    def start_backtest(self, strategy, data, params):
        worker = BacktestWorker(strategy, data, params)
        worker.signals.progress.connect(self.update_progress)
        worker.signals.finished.connect(self.on_backtest_complete)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)
    
    def start_optimization(self, strategy, data, param_ranges):
        worker = OptimizationWorker(strategy, data, param_ranges)
        worker.signals.progress.connect(self.update_optimization_progress)
        worker.signals.found_better.connect(self.update_best_params)
        worker.signals.finished.connect(self.on_optimization_complete)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)
```

---

## Data Flow

### Complete Interaction Sequence

```
User Action: Select Stock & Fetch Data
│
└─> MainWindow.on_fetch_clicked()
    │
    ├─> Validate inputs (ticker, dates)
    │   └─> If invalid: Show error, return
    │
    ├─> Create DataDownloadWorker
    │   │
    │   ├─> Signal: progress(10%)
    │   │
    │   ├─> Check SQLite cache
    │   │   ├─> Cache hit: Load data
    │   │   ├─> Cache miss: Download from yfinance
    │   │   │   └─> Signal: progress(70%)
    │   │   │
    │   │   └─> Store in cache
    │   │       └─> Signal: progress(90%)
    │   │
    │   └─> Return DataFrame
    │       └─> Signal: finished(data)
    │
    └─> MainWindow.on_data_loaded(data)
        │
        ├─> Update ApplicationState.stock_data
        │
        ├─> Enable Tab 1 (Strategy Selection)
        │
        ├─> Switch to Tab 1
        │
        ├─> Emit: dataLoadedSignal
        │
        └─> Update status bar


User Action: Configure Strategy & Click Run Backtest
│
└─> MainWindow.on_run_backtest_clicked()
    │
    ├─> Validate strategy parameters
    │   └─> If invalid: Show error dialog, return
    │
    ├─> Determine if optimization enabled
    │   │
    │   ├─ IF optimization disabled:
    │   │   └─> Create BacktestWorker(strategy, data, params)
    │   │       │
    │   │       ├─> Signal: progress(0%)
    │   │       │
    │   │       ├─> Run backtest
    │   │       │   └─> Signal: progress(50%)
    │   │       │
    │   │       ├─> Calculate metrics
    │   │       │   └─> Signal: progress(100%)
    │   │       │
    │   │       └─> Return results dict
    │   │           └─> Signal: finished(results)
    │   │
    │   └─ IF optimization enabled:
    │       └─> Create OptimizationWorker(strategy, data, param_ranges)
    │           │
    │           ├─> Generate parameter combinations (N combinations)
    │           │
    │           ├─> For i = 0 to N:
    │           │   │
    │           │   ├─> Run BacktestWorker(params[i])
    │           │   │   └─> Get return value
    │           │   │
    │           │   ├─> If return > best_return:
    │           │   │   └─> Signal: found_better(params, metrics)
    │           │   │       └─> Results tab updates live
    │           │   │
    │           │   └─> Signal: progress(i+1, N)
    │           │
    │           └─> Signal: finished(best_params, best_return)
    │
    └─> MainWindow.on_backtest_complete(results)
        │
        ├─> Update ApplicationState.backtest_results
        │
        ├─> Update ResultsAnalysisWidget
        │   │
        │   ├─> Populate metrics table
        │   │
        │   ├─> Draw cumulative returns chart
        │   │
        │   ├─> Draw indicators chart
        │   │
        │   └─> Draw buy/sell signals chart
        │
        ├─> Enable Tab 3 (Results)
        │
        ├─> Switch to Tab 3
        │
        └─> Update status bar
```

---

## Error Handling

### Error Handling Strategy

```python
class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def handle_error(error: Exception, context: str = ""):
        """Handle errors gracefully"""
        error_message = str(error)
        
        # Log error
        logger.error(f"{context}: {error_message}")
        
        # Show user-friendly message
        if isinstance(error, ValueError):
            user_message = f"Invalid input: {error_message}"
        elif isinstance(error, ConnectionError):
            user_message = "Network error. Check your internet connection."
        elif isinstance(error, KeyError):
            user_message = "Data error. Try a different stock or date range."
        else:
            user_message = f"An error occurred: {error_message}"
        
        return user_message
```

### Input Validation

```python
class InputValidator:
    """Validate user inputs"""
    
    @staticmethod
    def validate_ticker(ticker: str) -> Tuple[bool, str]:
        """Validate stock ticker"""
        if not ticker:
            return False, "Ticker cannot be empty"
        if not 1 <= len(ticker) <= 5:
            return False, "Ticker must be 1-5 characters"
        if not ticker.isalnum():
            return False, "Ticker must contain only letters and numbers"
        return True, ""
    
    @staticmethod
    def validate_date_range(start: QDate, end: QDate) -> Tuple[bool, str]:
        """Validate date range"""
        if start > end:
            return False, "Start date must be before end date"
        if (end.year() - start.year()) > 30:
            return False, "Date range cannot exceed 30 years"
        return True, ""
    
    @staticmethod
    def validate_strategy_params(strategy: str, params: dict) -> Tuple[bool, str]:
        """Validate strategy parameters"""
        param_specs = STRATEGY_PARAMS[strategy]
        
        for param_name, param_value in params.items():
            if param_name not in param_specs:
                return False, f"Unknown parameter: {param_name}"
            
            spec = param_specs[param_name]
            
            if spec['type'] == 'int':
                if not isinstance(param_value, int):
                    return False, f"{param_name} must be an integer"
                if not spec['min'] <= param_value <= spec['max']:
                    return False, f"{param_name} must be between {spec['min']} and {spec['max']}"
        
        return True, ""
```

---

## Styling & Themes

### Qt Stylesheet (Dark Theme)

```python
# src/ui/styles.py

DARK_STYLESHEET = """
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}

QTabWidget::pane {
    border: 1px solid #3d3d3d;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #ffffff;
    padding: 5px 15px;
    margin: 2px 2px 0px 0px;
}

QTabBar::tab:selected {
    background-color: #0d47a1;
    color: #ffffff;
}

QGroupBox {
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}

QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    padding: 5px;
}

QPushButton {
    background-color: #0d47a1;
    color: #ffffff;
    border: none;
    border-radius: 3px;
    padding: 6px 12px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1565c0;
}

QPushButton:pressed {
    background-color: #0a3d91;
}

QTableWidget {
    background-color: #2d2d2d;
    color: #ffffff;
    gridline-color: #3d3d3d;
}

QHeaderView::section {
    background-color: #1e1e1e;
    color: #ffffff;
    padding: 5px;
    border: 1px solid #3d3d3d;
}

QProgressBar {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
}

QProgressBar::chunk {
    background-color: #0d47a1;
}
"""

LIGHT_STYLESHEET = """
[Similar but with light colors]
"""
```

---

## Interaction Flows

### Flow 1: Basic Backtest (No Optimization)

```
START
  │
  ├─→ [Stock Config Tab]
  │    ├─ Enter ticker: AAPL
  │    ├─ Select dates: 2023-01-01 to 2024-01-01
  │    └─ Click "Fetch Data"
  │         └─→ Download/Cache data
  │             └─→ Enable Strategy tab
  │
  ├─→ [Strategy Selection Tab]
  │    ├─ Select strategy: Momentum
  │    ├─ Accept default parameters
  │    └─ Click "Validate"
  │         └─→ Enable Optimization tab
  │
  ├─→ [Optimization Tab]
  │    ├─ Uncheck "Enable Optimization"
  │    └─ Click "Run Backtest"
  │         └─→ BacktestWorker starts
  │             ├─ Run backtest: ~1 second
  │             ├─ Calculate metrics: <1 second
  │             └─ Return results
  │
  ├─→ [Results Tab] (Auto-switch)
  │    ├─ Display metrics table
  │    ├─ Draw charts
  │    └─ Enable export buttons
  │
  └─→ User clicks "Export CSV"
      └─→ Save backtest_AAPL_20230101-20240101.csv
```

### Flow 2: Backtest with Optimization

```
START
  │
  ├─→ [Optimization Tab]
  │    ├─ Check "Enable Optimization"
  │    ├─ Set momentum_period range: 8-20 (step 1) = 13 values
  │    ├─ Set mfi_level range: 40-60 (step 5) = 5 values
  │    ├─ Set stop_loss range: 3-10 (step 1%) = 8 values
  │    │  Total combinations: 13 × 5 × 8 = 520
  │    │  Est. time: 5-10 minutes
  │    │
  │    └─ Click "Start Optimization"
  │         └─→ OptimizationWorker starts
  │             │
  │             ├─ Iterate through 520 combinations
  │             │  ├─ For each: Run BacktestWorker
  │             │  ├─ Track best parameters & return
  │             │  │   └─ Real-time update: "found_better" signal
  │             │  │       └─ Results tab shows current best
  │             │  └─ Progress: 1/520, 2/520, ... 520/520
  │             │
  │             └─ Return best parameters & metrics
  │
  ├─→ [Results Tab] (Auto-switch)
  │    ├─ Display optimal parameters
  │    ├─ Display best metrics
  │    ├─ Show improvement vs defaults
  │    └─ Charts show trades with optimal parameters
  │
  └─→ User clicks "Generate PDF Report"
      └─→ Create detailed report with all findings
```

---

## Widget Initialization Example

```python
# Example: Creating StockConfigWidget

class StockConfigWidget(QWidget):
    # Signals
    data_ready = Signal(pd.DataFrame)
    download_started = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = None
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Stock input group
        stock_group = QGroupBox("Stock Selection")
        stock_layout = QFormLayout()
        
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("Enter ticker (e.g., AAPL, MSFT, TSLA)")
        stock_layout.addRow("Stock Ticker:", self.ticker_input)
        
        stock_group.setLayout(stock_layout)
        layout.addWidget(stock_group)
        
        # Date range group
        date_group = QGroupBox("Date Range")
        date_layout = QFormLayout()
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addYears(-2))
        self.start_date_edit.setCalendarPopup(True)
        date_layout.addRow("Start Date:", self.start_date_edit)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        date_layout.addRow("End Date:", self.end_date_edit)
        
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)
        
        # Options
        options_layout = QHBoxLayout()
        self.use_cache_checkbox = QCheckBox("Use Cached Data")
        self.use_cache_checkbox.setChecked(True)
        options_layout.addWidget(self.use_cache_checkbox)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.fetch_button = QPushButton("Fetch Data from yfinance")
        self.fetch_button.clicked.connect(self.on_fetch_clicked)
        button_layout.addWidget(self.fetch_button)
        
        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.clicked.connect(self.on_clear_cache_clicked)
        button_layout.addWidget(self.clear_cache_button)
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)
        
        # Preview
        preview_group = QGroupBox("Data Preview")
        self.preview_label = QLabel("No data loaded")
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def setup_connections(self):
        """Connect signals"""
        # ... connect signals
        pass
    
    def on_fetch_clicked(self):
        """Handle fetch button click"""
        # Validate inputs
        ticker = self.ticker_input.text().strip().upper()
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()
        
        is_valid, message = InputValidator.validate_ticker(ticker)
        if not is_valid:
            self.error_occurred.emit(message)
            return
        
        is_valid, message = InputValidator.validate_date_range(start_date, end_date)
        if not is_valid:
            self.error_occurred.emit(message)
            return
        
        # Start download worker
        self.download_started.emit()
        self.progress_bar.setVisible(True)
        
        # Create and start worker
        # ... worker logic
```

---

**End of GUI Architecture Document**

This detailed GUI architecture provides the foundation for implementing a professional, responsive trading strategy analysis application with PySide6.
