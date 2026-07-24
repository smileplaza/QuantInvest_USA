# QuantInvest Tool - UI 구현 가이드

## 개발자를 위한 빠른 참조

이 가이드는 PySide6를 사용하여 QuantInvest Tool UI를 구축하기 위한 코드 예제, 패턴, 단계별 지시사항을 제공합니다.

---

## 1부: 프로젝트 설정

### 1.1 UI 모듈 구조 생성

```
src/
├── ui/
│   ├── __init__.py                 # UI 모듈 초기화
│   ├── main_window.py              # 메인 애플리케이션 창
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── stock_config_widget.py  # 주식 설정 위젯
│   │   ├── strategy_widget.py      # 전략 선택 위젯
│   │   ├── optimization_widget.py  # 최적화 위젯
│   │   └── results_widget.py       # 결과 분석 위젯
│   ├── dialogs/
│   │   ├── __init__.py
│   │   ├── error_dialog.py         # 에러 대화상자
│   │   ├── progress_dialog.py      # 진행 대화상자
│   │   ├── parameter_dialog.py     # 파라미터 대화상자
│   │   └── export_dialog.py        # 내보내기 대화상자
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py           # 입력 검증
│   │   ├── formatting.py           # 형식 지정
│   │   └── widgets.py              # 재사용 가능한 위젯
│   ├── styles.py                   # 스타일시트
│   └── resources.py                # 아이콘, 리소스
```

### 1.2 PySide6 애플리케이션 초기화

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

## 2부: 메인 윈도우 구조

### 2.1 메인 윈도우 클래스

```python
# src/ui/main_window.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QTabWidget, QStatusBar, QMenuBar)
from PySide6.QtCore import Qt, Signal, QThreadPool

from .widgets.stock_config_widget import StockConfigWidget
from .widgets.strategy_widget import StrategySelectionWidget
from .widgets.optimization_widget import OptimizationWidget
from .widgets.results_widget import ResultsAnalysisWidget
from .styles import load_stylesheet

class ApplicationState:
    """중앙 애플리케이션 상태 관리"""
    def __init__(self):
        self.stock_ticker = None
        self.start_date = None
        self.end_date = None
        self.stock_data = None
        self.strategy_name = "모멘텀"
        self.strategy_params = {}
        self.backtest_results = None

class MainWindow(QMainWindow):
    """메인 애플리케이션 창"""
    
    # 커스텀 신호
    data_loaded = Signal(object)
    backtest_started = Signal()
    backtest_complete = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QuantInvest Tool v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # 스레드 풀
        self.thread_pool = QThreadPool()
        
        # 애플리케이션 상태
        self.state = ApplicationState()
        
        # UI 초기화
        self.init_ui()
        self.setup_connections()
        self.apply_stylesheet()
    
    def init_ui(self):
        """UI 컴포넌트 초기화"""
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 탭 위젯 생성
        self.tabs = QTabWidget()
        self.stock_config_tab = StockConfigWidget(self.state)
        self.strategy_tab = StrategySelectionWidget(self.state)
        self.optimization_tab = OptimizationWidget(self.state)
        self.results_tab = ResultsAnalysisWidget(self.state)
        
        # 탭 추가
        self.tabs.addTab(self.stock_config_tab, "주식 설정")
        self.tabs.addTab(self.strategy_tab, "전략 선택")
        self.tabs.addTab(self.optimization_tab, "최적화 설정")
        self.tabs.addTab(self.results_tab, "결과 & 분석")
        
        # 처음에는 탭 1-3 비활성화
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        self.tabs.setTabEnabled(3, False)
        
        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # 메뉴 바 생성
        self.create_menu_bar()
        
        # 상태 표시줄
        self.status_bar_label = QLabel("세션: 미저장 | 캐시: 준비됨")
        self.statusBar().addWidget(self.status_bar_label)
    
    def create_menu_bar(self):
        """메뉴 바 생성"""
        menu_bar = self.menuBar()
        
        # 파일 메뉴
        file_menu = menu_bar.addMenu("파일")
        file_menu.addAction("새 세션", self.new_session)
        file_menu.addAction("세션 열기", self.open_session)
        file_menu.addAction("세션 저장", self.save_session)
        file_menu.addSeparator()
        file_menu.addAction("결과 내보내기", self.export_results)
        file_menu.addSeparator()
        file_menu.addAction("종료", self.close)
        
        # 도움말 메뉴
        help_menu = menu_bar.addMenu("도움말")
        help_menu.addAction("정보", self.show_about)
        help_menu.addAction("문서", self.show_documentation)
    
    def setup_connections(self):
        """신호와 슬롯 연결"""
        self.stock_config_tab.data_ready.connect(self.on_data_loaded)
        self.stock_config_tab.error_occurred.connect(self.show_error)
        
        self.strategy_tab.parameters_validated.connect(self.on_params_validated)
        self.strategy_tab.error_occurred.connect(self.show_error)
        
        self.optimization_tab.optimization_started.connect(self.on_optimization_started)
        self.optimization_tab.optimization_complete.connect(self.on_optimization_complete)
        self.optimization_tab.error_occurred.connect(self.show_error)
    
    def apply_stylesheet(self):
        """다크 테마 스타일시트 적용"""
        stylesheet = load_stylesheet("dark")
        self.setStyleSheet(stylesheet)
    
    # 슬롯
    def on_data_loaded(self, data):
        """데이터 로드 신호 처리"""
        self.state.stock_data = data
        self.tabs.setTabEnabled(1, True)
        self.tabs.setCurrentIndex(1)
        self.status_bar_label.setText("데이터 로드 완료")
    
    def on_params_validated(self, params):
        """파라미터 검증 신호 처리"""
        self.state.strategy_params = params
        self.tabs.setTabEnabled(2, True)
    
    def on_optimization_started(self):
        """최적화 시작 처리"""
        self.status_bar_label.setText("최적화 진행 중...")
        self.tabs.setEnabled(False)
    
    def on_optimization_complete(self, results):
        """최적화 완료 처리"""
        self.state.backtest_results = results
        self.status_bar_label.setText("최적화 완료!")
        self.tabs.setEnabled(True)
        self.tabs.setTabEnabled(3, True)
        self.tabs.setCurrentIndex(3)
        self.backtest_complete.emit(results)
    
    def show_error(self, message):
        """에러 대화상자 표시"""
        from .dialogs.error_dialog import ErrorDialog
        dialog = ErrorDialog(message, parent=self)
        dialog.exec()
```

---

## 3부: 탭 구현

### 3.1 주식 설정 탭

```python
# src/ui/widgets/stock_config_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QGroupBox,
                             QLineEdit, QDateEdit, QCheckBox, QPushButton,
                             QProgressBar, QLabel)
from PySide6.QtCore import Signal, Slot, QDate

class StockConfigWidget(QWidget):
    """주식 설정 및 데이터 다운로드 위젯"""
    
    # 신호
    data_ready = Signal(object)  # DataFrame
    download_started = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """UI 컴포넌트 초기화"""
        layout = QVBoxLayout()
        
        # 주식 선택 그룹
        stock_group = QGroupBox("주식 선택")
        stock_layout = QFormLayout()
        
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("티커 입력 (예: AAPL, MSFT, TSLA)")
        stock_layout.addRow("주식 티커:", self.ticker_input)
        
        stock_group.setLayout(stock_layout)
        layout.addWidget(stock_group)
        
        # 날짜 범위 그룹
        date_group = QGroupBox("날짜 범위")
        date_layout = QFormLayout()
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addYears(-2))
        self.start_date_edit.setCalendarPopup(True)
        date_layout.addRow("시작 날짜:", self.start_date_edit)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        date_layout.addRow("종료 날짜:", self.end_date_edit)
        
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)
        
        # 버튼
        self.fetch_button = QPushButton("Yahoo Finance에서 데이터 다운로드")
        self.fetch_button.clicked.connect(self.on_fetch_clicked)
        layout.addWidget(self.fetch_button)
        
        # 진행률 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 데이터 미리보기
        preview_group = QGroupBox("데이터 미리보기")
        self.preview_label = QLabel("데이터 로드 안 됨")
        layout.addWidget(preview_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    @Slot()
    def on_fetch_clicked(self):
        """다운로드 버튼 클릭 처리"""
        ticker = self.ticker_input.text().strip().upper()
        
        # 입력 검증
        from ui.utils.validators import InputValidator
        is_valid, message = InputValidator.validate_ticker(ticker)
        if not is_valid:
            self.error_occurred.emit(message)
            return
        
        # 데이터 다운로드 시작
        self.progress_bar.setVisible(True)
        
        # 워커 생성 및 시작
        from data.downloader import DataDownloadWorker
        worker = DataDownloadWorker(ticker, self.start_date_edit.date(), 
                                   self.end_date_edit.date())
        worker.signals.progress.connect(self.update_progress)
        worker.signals.finished.connect(self.on_data_downloaded)
        worker.signals.error.connect(self.on_download_error)
```

---

## 4부: 검증 & 형식 지정

### 4.1 검증 모듈

```python
# src/ui/utils/validators.py
from PySide6.QtCore import QDate

class InputValidator:
    """입력 검증 유틸리티 클래스"""
    
    @staticmethod
    def validate_ticker(ticker: str):
        """주식 티커 검증"""
        if not ticker:
            return False, "티커를 입력해주세요"
        
        if not (1 <= len(ticker) <= 5):
            return False, "티커는 1-5자여야 합니다"
        
        if not ticker.isalnum():
            return False, "티커는 영문자와 숫자만 포함해야 합니다"
        
        return True, ""
    
    @staticmethod
    def validate_date_range(start: QDate, end: QDate):
        """날짜 범위 검증"""
        if start > end:
            return False, "시작 날짜는 종료 날짜보다 빨라야 합니다"
        
        years_diff = end.year() - start.year()
        if years_diff > 30:
            return False, "날짜 범위는 30년을 초과할 수 없습니다"
        
        return True, ""


class NumberFormatter:
    """숫자 형식 지정"""
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """백분율로 형식화"""
        return f"{value * 100:.{decimals}f}%"
    
    @staticmethod
    def format_number(value: float, decimals: int = 2) -> str:
        """천 단위 쉼표 포함하여 형식화"""
        return f"{value:,.{decimals}f}"
```

---

## 5부: 스타일링

### 5.1 스타일시트 모듈

```python
# src/ui/styles.py

DARK_STYLESHEET = """
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #ffffff;
    padding: 5px 15px;
}

QTabBar::tab:selected {
    background-color: #0d47a1;
    color: #ffffff;
}

QPushButton {
    background-color: #0d47a1;
    color: #ffffff;
    border: none;
    border-radius: 3px;
    padding: 6px 12px;
    min-height: 36px;
}

QPushButton:hover {
    background-color: #1565c0;
}

QPushButton:pressed {
    background-color: #0a3d91;
}

QLineEdit, QDateEdit {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    padding: 5px;
}

QLineEdit:focus, QDateEdit:focus {
    border: 2px solid #0d47a1;
}

QGroupBox {
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}

QProgressBar {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
}

QProgressBar::chunk {
    background-color: #0d47a1;
    border-radius: 2px;
}
"""

def load_stylesheet(theme: str = "dark") -> str:
    """주어진 테마의 스타일시트 로드"""
    if theme == "dark":
        return DARK_STYLESHEET
    return DARK_STYLESHEET
```

---

## 새 위젯 빌드 템플릿

```python
# 새로운 위젯의 템플릿
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal

class MyNewWidget(QWidget):
    """위젯 설명"""
    
    # 신호 정의
    value_changed = Signal(object)
    error_occurred = Signal(str)
    
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """UI 컴포넌트 초기화"""
        layout = QVBoxLayout()
        # 레이아웃에 위젯 추가
        self.setLayout(layout)
    
    def setup_connections(self):
        """신호와 슬롯 연결"""
        pass
    
    # 커스텀 메서드와 슬롯 구현
```

---

**PySide6를 사용하여 QuantInvest Tool UI를 구축하기 위한 이 구현 가이드는 일관성 있고 유지보수하기 쉬운 코드를 제공합니다.**
