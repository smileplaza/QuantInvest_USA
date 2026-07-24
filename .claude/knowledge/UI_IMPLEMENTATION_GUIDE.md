# QuantInvest Tool - UI Implementation Guide

## Quick Reference for Developers

This guide provides code examples, patterns, and step-by-step instructions for building the QuantInvest Tool UI with PySide6.

---

## Part 1: Project Setup

### Step 1.1: Create UI Module Structure

```
src/
├── ui/
│   ├── __init__.py                 # UI module init
│   ├── main_window.py              # Main application window
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── stock_config_widget.py
│   │   ├── strategy_widget.py
│   │   ├── optimization_widget.py
│   │   └── results_widget.py
│   ├── dialogs/
│   │   ├── __init__.py
│   │   ├── error_dialog.py
│   │   ├── progress_dialog.py
│   │   ├── parameter_dialog.py
│   │   └── export_dialog.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py           # Input validation
│   │   ├── formatting.py           # Format numbers, dates
│   │   └── widgets.py              # Reusable widget components
│   ├── styles.py                   # Stylesheets
│   └── resources.py                # Icons, resources
```

### Step 1.2: Initialize PySide6 Application

```python
# src/main.py
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("QuantInvest Tool")
    app.setApplicationVersion("1.0.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

---

## Part 2: Main Window Structure

### Step 2.1: Create Main Window Class

```python
# src/ui/main_window.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QTabWidget, QStatusBar, QMenuBar, 
                             QProgressBar, QPushButton, QLabel)
from PySide6.QtCore import Qt, Signal, QThreadPool

from .widgets.stock_config_widget import StockConfigWidget
from .widgets.strategy_widget import StrategySelectionWidget
from .widgets.optimization_widget import OptimizationWidget
from .widgets.results_widget import ResultsAnalysisWidget
from .styles import load_stylesheet

class MainWindow(QMainWindow):
    """Main application window"""
    
    # Custom signals
    data_loaded = Signal(object)  # DataFrame
    backtest_started = Signal()
    backtest_complete = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QuantInvest Tool v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # Thread pool for workers
        self.thread_pool = QThreadPool()
        
        # Application state
        self.state = ApplicationState()
        
        # Initialize UI
        self.init_ui()
        self.setup_connections()
        self.apply_stylesheet()
    
    def init_ui(self):
        """Initialize UI components"""
        # Create central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.stock_config_tab = StockConfigWidget(self.state)
        self.strategy_tab = StrategySelectionWidget(self.state)
        self.optimization_tab = OptimizationWidget(self.state)
        self.results_tab = ResultsAnalysisWidget(self.state)
        
        self.tabs.addTab(self.stock_config_tab, "Stock Configuration")
        self.tabs.addTab(self.strategy_tab, "Strategy Selection")
        self.tabs.addTab(self.optimization_tab, "Optimization Settings")
        self.tabs.addTab(self.results_tab, "Results & Analysis")
        
        # Disable tabs 1-3 initially
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        self.tabs.setTabEnabled(3, False)
        
        main_layout.addWidget(self.tabs)
        
        # Control bar
        control_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_label = QLabel("Ready")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setVisible(False)
        
        control_layout.addWidget(self.progress_bar)
        control_layout.addWidget(self.status_label)
        control_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(control_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar_label = QLabel("Session: Unsaved | Cache: Ready")
        self.statusBar().addWidget(self.status_bar_label)
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("New Session", self.new_session)
        file_menu.addAction("Open Session", self.open_session)
        file_menu.addAction("Save Session", self.save_session)
        file_menu.addSeparator()
        file_menu.addAction("Export Results", self.export_results)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About", self.show_about)
        help_menu.addAction("Documentation", self.show_documentation)
        help_menu.addAction("Settings", self.show_settings)
    
    def setup_connections(self):
        """Connect signals and slots"""
        # Tab signals
        self.stock_config_tab.data_ready.connect(self.on_data_loaded)
        self.stock_config_tab.error_occurred.connect(self.show_error)
        
        self.strategy_tab.parameters_validated.connect(self.on_params_validated)
        self.strategy_tab.error_occurred.connect(self.show_error)
        
        self.optimization_tab.optimization_started.connect(self.on_optimization_started)
        self.optimization_tab.optimization_complete.connect(self.on_optimization_complete)
        self.optimization_tab.error_occurred.connect(self.show_error)
        
        self.cancel_button.clicked.connect(self.cancel_operation)
        self.tabs.currentChanged.connect(self.on_tab_changed)
    
    def apply_stylesheet(self):
        """Apply dark theme stylesheet"""
        stylesheet = load_stylesheet("dark")
        self.setStyleSheet(stylesheet)
    
    # Slots
    def on_data_loaded(self, data):
        """Handle data loaded signal"""
        self.state.stock_data = data
        self.tabs.setTabEnabled(1, True)
        self.tabs.setCurrentIndex(1)
        self.status_label.setText("Data loaded successfully")
        self.data_loaded.emit(data)
    
    def on_params_validated(self, params):
        """Handle parameters validated signal"""
        self.state.strategy_params = params
        self.tabs.setTabEnabled(2, True)
        self.status_label.setText("Parameters valid - Ready to optimize or backtest")
    
    def on_optimization_started(self):
        """Handle optimization start"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Optimization in progress...")
        self.cancel_button.setVisible(True)
        self.tabs.setEnabled(False)
    
    def on_optimization_complete(self, results):
        """Handle optimization complete"""
        self.state.backtest_results = results
        self.progress_bar.setVisible(False)
        self.status_label.setText("Optimization complete!")
        self.cancel_button.setVisible(False)
        self.tabs.setEnabled(True)
        self.tabs.setTabEnabled(3, True)
        self.tabs.setCurrentIndex(3)
        self.backtest_complete.emit(results)
    
    def on_tab_changed(self, index):
        """Handle tab change"""
        if index == 0:
            self.status_label.setText("Select stock and date range")
        elif index == 1:
            self.status_label.setText("Configure strategy parameters")
        elif index == 2:
            self.status_label.setText("Set optimization ranges")
        elif index == 3:
            self.status_label.setText("View results and analysis")
    
    def show_error(self, message):
        """Show error dialog"""
        from .dialogs.error_dialog import ErrorDialog
        dialog = ErrorDialog(message, parent=self)
        dialog.exec()
    
    def cancel_operation(self):
        """Cancel current operation"""
        self.progress_bar.setVisible(False)
        self.cancel_button.setVisible(False)
        self.status_label.setText("Operation cancelled")
        self.tabs.setEnabled(True)
    
    def new_session(self):
        """Create new session"""
        self.state = ApplicationState()
        self.status_bar_label.setText("Session: Unsaved | Cache: Ready")
    
    def open_session(self):
        """Open saved session"""
        pass  # Implement session loading
    
    def save_session(self):
        """Save current session"""
        pass  # Implement session saving
    
    def export_results(self):
        """Export results"""
        from .dialogs.export_dialog import ExportDialog
        if self.state.backtest_results:
            dialog = ExportDialog(self.state, parent=self)
            dialog.exec()
    
    def show_about(self):
        """Show about dialog"""
        pass  # Implement about dialog
    
    def show_documentation(self):
        """Show documentation"""
        pass  # Implement documentation viewer
    
    def show_settings(self):
        """Show settings dialog"""
        pass  # Implement settings dialog


class ApplicationState:
    """Central application state management"""
    def __init__(self):
        self.stock_ticker = None
        self.start_date = None
        self.end_date = None
        self.stock_data = None
        self.strategy_name = "Momentum"
        self.strategy_params = {}
        self.backtest_results = None
        self.optimization_enabled = False
```

---

## Part 3: Tab Implementations

### Step 3.1: Stock Configuration Tab

```python
# src/ui/widgets/stock_config_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QGroupBox,
                             QLineEdit, QDateEdit, QCheckBox, QPushButton,
                             QProgressBar, QLabel, QHBoxLayout)
from PySide6.QtCore import Signal, Slot, QDate, Qt
from PySide6.QtGui import QIcon

class StockConfigWidget(QWidget):
    """Stock configuration and data download widget"""
    
    # Signals
    data_ready = Signal(object)  # DataFrame
    download_started = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Stock selection group
        stock_group = QGroupBox("Stock Selection")
        stock_layout = QFormLayout()
        
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("Enter ticker (e.g., AAPL, MSFT, TSLA)")
        self.ticker_input.setMinimumWidth(200)
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
        self.use_cache_checkbox = QCheckBox("Use Cached Data (if available)")
        self.use_cache_checkbox.setChecked(True)
        options_layout.addWidget(self.use_cache_checkbox)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.fetch_button = QPushButton("Fetch Data from yfinance")
        self.fetch_button.setMinimumWidth(200)
        self.fetch_button.clicked.connect(self.on_fetch_clicked)
        button_layout.addWidget(self.fetch_button)
        
        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.setMinimumWidth(120)
        self.clear_cache_button.clicked.connect(self.on_clear_cache_clicked)
        button_layout.addWidget(self.clear_cache_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)
        
        # Data preview
        preview_group = QGroupBox("Data Preview")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel("No data loaded")
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def setup_connections(self):
        """Connect signals"""
        self.ticker_input.textChanged.connect(self.on_ticker_changed)
    
    @Slot()
    def on_fetch_clicked(self):
        """Handle fetch button click"""
        ticker = self.ticker_input.text().strip().upper()
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()
        
        # Validate inputs
        from ui.utils.validators import InputValidator
        is_valid, message = InputValidator.validate_ticker(ticker)
        if not is_valid:
            self.error_occurred.emit(message)
            return
        
        is_valid, message = InputValidator.validate_date_range(start_date, end_date)
        if not is_valid:
            self.error_occurred.emit(message)
            return
        
        # Show progress
        self.download_started.emit()
        self.progress_bar.setVisible(True)
        self.fetch_button.setEnabled(False)
        self.status_label.setText("Downloading data...")
        
        # Start download worker
        from data.downloader import DataDownloadWorker
        worker = DataDownloadWorker(ticker, start_date, end_date, 
                                   use_cache=self.use_cache_checkbox.isChecked())
        worker.signals.progress.connect(self.update_progress)
        worker.signals.finished.connect(self.on_data_downloaded)
        worker.signals.error.connect(self.on_download_error)
        
        # Use parent's thread pool if available
        parent = self.parent()
        if hasattr(parent, 'thread_pool'):
            parent.thread_pool.start(worker)
    
    @Slot(int)
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    @Slot(object)
    def on_data_downloaded(self, data):
        """Handle data downloaded"""
        self.progress_bar.setVisible(False)
        self.fetch_button.setEnabled(True)
        
        # Update preview
        rows, cols = data.shape
        self.preview_label.setText(
            f"Ticker: {self.ticker_input.text().upper()}\n"
            f"Date Range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}\n"
            f"Trading Days: {rows}\n"
            f"Columns: {', '.join(data.columns)}"
        )
        self.status_label.setText("Data loaded successfully!")
        
        # Emit signal
        self.data_ready.emit(data)
    
    @Slot(str)
    def on_download_error(self, error_message):
        """Handle download error"""
        self.progress_bar.setVisible(False)
        self.fetch_button.setEnabled(True)
        self.status_label.setText("Download failed!")
        self.error_occurred.emit(error_message)
    
    @Slot()
    def on_clear_cache_clicked(self):
        """Handle clear cache button"""
        from data.cache import CacheManager
        from ui.dialogs.confirmation_dialog import ConfirmationDialog
        
        dialog = ConfirmationDialog(
            "Clear Cache?",
            "This will delete all cached stock data. "
            "Downloaded data will need to be re-fetched.",
            parent=self
        )
        
        if dialog.exec():
            cache = CacheManager()
            cache.clear_all()
            self.status_label.setText("Cache cleared successfully!")
    
    @Slot(str)
    def on_ticker_changed(self, text):
        """Handle ticker input change"""
        # Could add auto-suggest here
        pass
```

---

## Part 4: Input Validation & Formatting

### Step 4.1: Validators Module

```python
# src/ui/utils/validators.py
from PySide6.QtCore import QDate
from datetime import datetime

class InputValidator:
    """Input validation utility class"""
    
    @staticmethod
    def validate_ticker(ticker: str):
        """Validate stock ticker"""
        if not ticker:
            return False, "Ticker cannot be empty"
        
        ticker = ticker.strip()
        if not (1 <= len(ticker) <= 5):
            return False, "Ticker must be 1-5 characters"
        
        if not ticker.isalnum():
            return False, "Ticker must contain only letters and numbers"
        
        return True, ""
    
    @staticmethod
    def validate_date_range(start: QDate, end: QDate):
        """Validate date range"""
        if start > end:
            return False, "Start date must be before end date"
        
        years_diff = end.year() - start.year()
        if years_diff > 30:
            return False, "Date range cannot exceed 30 years"
        
        return True, ""
    
    @staticmethod
    def validate_strategy_params(strategy: str, params: dict):
        """Validate strategy parameters"""
        from backtest.strategies import STRATEGY_PARAMS
        
        if strategy not in STRATEGY_PARAMS:
            return False, f"Unknown strategy: {strategy}"
        
        spec = STRATEGY_PARAMS[strategy]
        
        for param_name, param_value in params.items():
            if param_name not in spec:
                return False, f"Unknown parameter: {param_name}"
            
            param_spec = spec[param_name]
            
            # Type validation
            if param_spec.get('type') == 'int':
                if not isinstance(param_value, int):
                    return False, f"{param_name} must be an integer"
            elif param_spec.get('type') == 'float':
                if not isinstance(param_value, (int, float)):
                    return False, f"{param_name} must be a number"
            
            # Range validation
            if 'min' in param_spec and param_value < param_spec['min']:
                return False, f"{param_name} must be >= {param_spec['min']}"
            
            if 'max' in param_spec and param_value > param_spec['max']:
                return False, f"{param_name} must be <= {param_spec['max']}"
        
        return True, ""


class NumberFormatter:
    """Format numbers for display"""
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """Format as percentage"""
        return f"{value * 100:.{decimals}f}%"
    
    @staticmethod
    def format_currency(value: float, decimals: int = 2) -> str:
        """Format as currency"""
        return f"${value:,.{decimals}f}"
    
    @staticmethod
    def format_number(value: float, decimals: int = 2) -> str:
        """Format as number with comma separators"""
        return f"{value:,.{decimals}f}"
    
    @staticmethod
    def format_date(date: QDate) -> str:
        """Format date"""
        return date.toString("yyyy-MM-dd")
```

---

## Part 5: Styling Implementation

### Step 5.1: Stylesheet Module

```python
# src/ui/styles.py

DARK_STYLESHEET = """
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}

QWidget {
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
    min-width: 80px;
}

QTabBar::tab:selected {
    background-color: #0d47a1;
    color: #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #3d3d3d;
}

QGroupBox {
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}

QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    padding: 5px;
    min-height: 28px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
    border: 2px solid #0d47a1;
}

QPushButton {
    background-color: #0d47a1;
    color: #ffffff;
    border: none;
    border-radius: 3px;
    padding: 6px 12px;
    min-height: 36px;
    min-width: 80px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1565c0;
}

QPushButton:pressed {
    background-color: #0a3d91;
}

QPushButton:disabled {
    background-color: #9e9e9e;
    color: #666666;
}

QCheckBox, QRadioButton {
    color: #ffffff;
    spacing: 5px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 2px;
}

QCheckBox::indicator:checked {
    background-color: #0d47a1;
    border: 1px solid #0d47a1;
    border-radius: 2px;
}

QComboBox {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    padding: 5px;
    min-height: 28px;
}

QComboBox:focus {
    border: 2px solid #0d47a1;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(:/icons/down_arrow.png);
}

QTableWidget {
    background-color: #2d2d2d;
    color: #ffffff;
    gridline-color: #3d3d3d;
    border: 1px solid #3d3d3d;
}

QTableWidget::item {
    padding: 5px;
}

QTableWidget::item:selected {
    background-color: #0d47a1;
}

QHeaderView::section {
    background-color: #1e1e1e;
    color: #ffffff;
    padding: 5px;
    border: 1px solid #3d3d3d;
    font-weight: bold;
}

QProgressBar {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    text-align: center;
    color: #ffffff;
}

QProgressBar::chunk {
    background-color: #0d47a1;
    border-radius: 2px;
}

QLabel {
    color: #ffffff;
}

QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
    border: 1px solid #3d3d3d;
}

QScrollBar::handle:vertical {
    background-color: #3d3d3d;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4d4d4d;
}

QScrollBar:horizontal {
    background-color: #2d2d2d;
    height: 12px;
    border: 1px solid #3d3d3d;
}

QScrollBar::handle:horizontal {
    background-color: #3d3d3d;
    border-radius: 6px;
    min-width: 20px;
}

QStatusBar {
    background-color: #2d2d2d;
    border-top: 1px solid #3d3d3d;
}

QMenuBar {
    background-color: #2d2d2d;
    color: #ffffff;
    border-bottom: 1px solid #3d3d3d;
}

QMenuBar::item:selected {
    background-color: #3d3d3d;
}

QMenu {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
}

QMenu::item:selected {
    background-color: #0d47a1;
}
"""

LIGHT_STYLESHEET = """
[Similar structure with light colors...]
"""

def load_stylesheet(theme: str = "dark") -> str:
    """Load stylesheet for given theme"""
    if theme == "dark":
        return DARK_STYLESHEET
    elif theme == "light":
        return LIGHT_STYLESHEET
    else:
        return DARK_STYLESHEET
```

---

## Part 6: Error Handling & Dialogs

### Step 6.1: Error Dialog

```python
# src/ui/dialogs/error_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class ErrorDialog(QDialog):
    """Error message dialog"""
    
    def __init__(self, message: str, title: str = "Error", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Error message
        label = QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
```

---

## Part 7: Testing UI Components

### Step 7.1: Basic UI Test

```python
# tests/test_ui.py
import sys
import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def app():
    """Create QApplication for tests"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
        yield app
        app.quit()
    else:
        yield QApplication.instance()

def test_main_window_creation(app):
    """Test main window creation"""
    from ui.main_window import MainWindow
    window = MainWindow()
    assert window.windowTitle() == "QuantInvest Tool v1.0"
    assert window.width() >= 800
    assert window.height() >= 600
    window.close()

def test_tab_disabled_on_startup(app):
    """Test that tabs are disabled on startup"""
    from ui.main_window import MainWindow
    window = MainWindow()
    assert not window.tabs.isTabEnabled(1)
    assert not window.tabs.isTabEnabled(2)
    assert not window.tabs.isTabEnabled(3)
    window.close()
```

---

## Quick Reference: Building a New Widget

```python
# Template for new widget
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Signal

class MyNewWidget(QWidget):
    """Description of widget"""
    
    # Define signals
    value_changed = Signal(object)
    error_occurred = Signal(str)
    
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        # Add widgets to layout
        self.setLayout(layout)
    
    def setup_connections(self):
        """Connect signals and slots"""
        pass
    
    # Implement custom methods and slots
```

---

**This implementation guide provides concrete examples for building the QuantInvest Tool UI. Follow these patterns for consistency and maintainability.**
