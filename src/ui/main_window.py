"""
QuantInvest Tool - Main Application Window
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QStatusBar, QMenuBar, QProgressBar,
                               QPushButton, QLabel, QMessageBox, QLineEdit, QComboBox,
                               QSpinBox, QDoubleSpinBox, QCheckBox, QTableWidget,
                               QTableWidgetItem, QTextEdit, QCalendarWidget, QFileDialog)
from PySide6.QtCore import Signal, QDate, QThread
from PySide6.QtGui import QFont, QKeySequence, QAction
import logging
from .dialogs import (DateRangeDialog, ParameterRangeDialog, ChartDialog,
                      ResultsTableWidget, SettingsDialog, FAQDialog)
from .styles import apply_stylesheet
from .utils.validators import InputValidator
from .utils.formatting import MetricFormatter
from .utils.settings import AppSettings
from data.downloader import DataDownloader, DataDownloadWorker, DataDownloadSignals
from data.cache import CacheManager
from backtest.engine import BacktestEngine
from backtest.optimizer import ParameterOptimizer
from strategies.momentum_strategy import MomentumStrategy
from strategies.trend_following import TrendFollowingStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.portfolio import PortfolioStrategy
from utils.plotting import plot_cumulative_returns, plot_indicators, plot_buy_sell_signals
from utils.report import export_backtest_pdf
import pandas as pd

logger = logging.getLogger(__name__)


class ApplicationState:
    """중앙 애플리케이션 상태 관리"""

    def __init__(self):
        self.stock_ticker = None
        self.start_date = None
        self.end_date = None
        self.stock_data = None
        self.strategy_name = None
        self.strategy_params = {}
        self.backtest_results = {}
        self.optimization_settings = {}


class MainWindow(QMainWindow):
    """QuantInvest Tool 메인 애플리케이션 윈도우"""

    # 커스텀 신호
    data_loaded = Signal(object)
    backtest_started = Signal()
    backtest_complete = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QuantInvest Tool - 정량 투자 전략 분석")
        self.setGeometry(100, 100, 1400, 900)

        self.state = ApplicationState()
        self.settings = AppSettings()
        self.cache_manager = CacheManager()
        self.engine = BacktestEngine(
            initial_capital=self.settings.get('initial_capital'),
            transaction_fee=self.settings.get('transaction_fee'),
        )
        self.optimizer = ParameterOptimizer(use_parallel=self.settings.get('use_parallel'))
        self.download_worker = None

        self.init_ui()
        self.create_menu()
        self.create_shortcuts()
        apply_stylesheet(self, theme=self.settings.get('theme'))

        logger.info("QuantInvest Tool 시작됨")

    def _rebuild_engine_from_settings(self):
        """설정 변경 후 엔진/최적화기를 새 값으로 재구성."""
        self.engine = BacktestEngine(
            initial_capital=self.settings.get('initial_capital'),
            transaction_fee=self.settings.get('transaction_fee'),
        )
        self.optimizer.use_parallel = self.settings.get('use_parallel')

    def init_ui(self):
        """UI 초기화"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tab1 = self.create_tab1_stock_config()
        self.tab2 = self.create_tab2_strategy_selection()
        self.tab3 = self.create_tab3_optimization()
        self.tab4 = self.create_tab4_results()

        self.tabs.addTab(self.tab1, "주식 및 날짜 설정")
        self.tabs.addTab(self.tab2, "전략 선택 및 파라미터")
        self.tabs.addTab(self.tab3, "최적화 설정")
        self.tabs.addTab(self.tab4, "결과 분석")

        main_layout.addWidget(self.tabs)

        self.status_label = QLabel("준비 완료")
        self.statusBar().addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar, 1)

        central_widget.setLayout(main_layout)

    def create_tab1_stock_config(self):
        """탭 1: 주식 및 날짜 설정"""
        widget = QWidget()
        layout = QVBoxLayout()

        ticker_layout = QHBoxLayout()
        ticker_label = QLabel("주식 티커:")
        ticker_label.setFixedWidth(100)
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("예: AAPL, MSFT, GOOGL")
        ticker_layout.addWidget(ticker_label)
        ticker_layout.addWidget(self.ticker_input)
        layout.addLayout(ticker_layout)

        date_layout = QHBoxLayout()
        date_label = QLabel("날짜 범위:")
        date_label.setFixedWidth(100)
        self.date_display = QLabel("미설정")
        date_button = QPushButton("날짜 선택")
        date_button.clicked.connect(self.on_date_selection)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_display)
        date_layout.addWidget(date_button)
        layout.addLayout(date_layout)

        download_layout = QHBoxLayout()
        self.download_button = QPushButton("데이터 다운로드")
        self.download_button.clicked.connect(self.on_download_data)
        download_layout.addWidget(self.download_button)
        download_layout.addStretch()
        layout.addLayout(download_layout)

        cache_layout = QHBoxLayout()
        self.cache_info = QLabel("캐시: 비어있음")
        cache_clear_button = QPushButton("캐시 삭제")
        cache_clear_button.clicked.connect(self.on_clear_cache)
        cache_layout.addWidget(self.cache_info)
        cache_layout.addWidget(cache_clear_button)
        cache_layout.addStretch()
        layout.addLayout(cache_layout)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_tab2_strategy_selection(self):
        """탭 2: 전략 선택 및 파라미터"""
        widget = QWidget()
        layout = QVBoxLayout()

        strategy_layout = QHBoxLayout()
        strategy_label = QLabel("전략 선택:")
        strategy_label.setFixedWidth(100)
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "Momentum Strategy",
            "Trend Following Strategy",
            "Mean Reversion Strategy",
            "Portfolio Strategy"
        ])
        self.strategy_combo.currentTextChanged.connect(self.on_strategy_changed)
        strategy_layout.addWidget(strategy_label)
        strategy_layout.addWidget(self.strategy_combo)
        strategy_layout.addStretch()
        layout.addLayout(strategy_layout)

        params_label = QLabel("전략 파라미터:")
        params_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(params_label)

        self.params_layout = QVBoxLayout()
        self.param_inputs = {}
        self.update_parameters_ui()

        layout.addLayout(self.params_layout)

        backtest_layout = QHBoxLayout()
        self.backtest_button = QPushButton("백테스트 실행")
        self.backtest_button.clicked.connect(self.on_run_backtest)
        backtest_layout.addWidget(self.backtest_button)
        backtest_layout.addStretch()
        layout.addLayout(backtest_layout)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_tab3_optimization(self):
        """탭 3: 최적화 설정"""
        widget = QWidget()
        layout = QVBoxLayout()

        self.optimization_checkbox = QCheckBox("파라미터 최적화 실행")
        layout.addWidget(self.optimization_checkbox)

        range_layout = QHBoxLayout()
        range_label = QLabel("파라미터 범위:")
        range_label.setFixedWidth(100)
        self.set_ranges_button = QPushButton("범위 설정")
        self.set_ranges_button.clicked.connect(self.on_set_ranges)
        self.ranges_display = QLabel("미설정")
        range_layout.addWidget(range_label)
        range_layout.addWidget(self.set_ranges_button)
        range_layout.addWidget(self.ranges_display)
        range_layout.addStretch()
        layout.addLayout(range_layout)

        parallel_layout = QHBoxLayout()
        self.parallel_checkbox = QCheckBox("병렬 처리 사용")
        parallel_layout.addWidget(self.parallel_checkbox)
        parallel_layout.addStretch()
        layout.addLayout(parallel_layout)

        optimize_layout = QHBoxLayout()
        self.optimize_button = QPushButton("최적화 시작")
        self.optimize_button.clicked.connect(self.on_run_optimization)
        optimize_layout.addWidget(self.optimize_button)
        optimize_layout.addStretch()
        layout.addLayout(optimize_layout)

        self.optimization_results = ResultsTableWidget()
        layout.addWidget(QLabel("최적화 결과:"))
        layout.addWidget(self.optimization_results)

        widget.setLayout(layout)
        return widget

    def create_tab4_results(self):
        """탭 4: 결과 분석"""
        widget = QWidget()
        layout = QVBoxLayout()

        metrics_label = QLabel("성능 지표:")
        metrics_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(metrics_label)

        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["지표", "값"])
        self.metrics_table.setColumnWidth(0, 150)
        self.metrics_table.setColumnWidth(1, 200)
        layout.addWidget(self.metrics_table)

        chart_layout = QHBoxLayout()
        self.chart_returns_button = QPushButton("누적 수익률 차트")
        self.chart_returns_button.clicked.connect(self.on_show_chart_returns)
        self.chart_indicators_button = QPushButton("지표 차트")
        self.chart_indicators_button.clicked.connect(self.on_show_chart_indicators)
        self.chart_signals_button = QPushButton("매매 신호 차트")
        self.chart_signals_button.clicked.connect(self.on_show_chart_signals)

        chart_layout.addWidget(self.chart_returns_button)
        chart_layout.addWidget(self.chart_indicators_button)
        chart_layout.addWidget(self.chart_signals_button)
        chart_layout.addStretch()
        layout.addLayout(chart_layout)

        report_label = QLabel("상세 보고서:")
        report_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(report_label)

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)

        export_layout = QHBoxLayout()
        export_csv_button = QPushButton("CSV로 내보내기")
        export_csv_button.clicked.connect(self.on_export_csv)
        export_report_button = QPushButton("보고서 저장")
        export_report_button.clicked.connect(self.on_export_report)
        export_pdf_button = QPushButton("PDF로 내보내기")
        export_pdf_button.clicked.connect(self.on_export_pdf)

        export_layout.addWidget(export_csv_button)
        export_layout.addWidget(export_report_button)
        export_layout.addWidget(export_pdf_button)
        export_layout.addStretch()
        layout.addLayout(export_layout)

        widget.setLayout(layout)
        return widget

    def create_menu(self):
        """메뉴 바 생성"""
        menubar = self.menuBar()

        file_menu = menubar.addMenu("파일")
        self.act_settings = QAction("설정...", self)
        self.act_settings.setShortcut(QKeySequence("Ctrl+,"))
        self.act_settings.triggered.connect(self.on_settings)
        file_menu.addAction(self.act_settings)
        file_menu.addSeparator()
        exit_action = QAction("종료", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("도움말")
        faq_action = QAction("자주 묻는 질문 (FAQ)", self)
        faq_action.setShortcut(QKeySequence("F1"))
        faq_action.triggered.connect(self.on_faq)
        help_menu.addAction(faq_action)
        about_action = QAction("정보", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def create_shortcuts(self):
        """전역 키보드 단축키 등록.

        메뉴에 없는 동작들을 QAction으로 윈도우에 추가한다. QAction 단축키는
        위젯 활성화 여부와 무관하게 윈도우 범위에서 동작한다.
        """
        shortcuts = [
            ("Ctrl+D", self.on_download_data),          # 데이터 다운로드
            ("Ctrl+R", self.on_run_backtest),           # 백테스트 실행
            ("Ctrl+Shift+O", self.on_run_optimization), # 최적화 시작
            ("Ctrl+E", self.on_export_csv),             # CSV 내보내기
            ("Ctrl+P", self.on_export_pdf),             # PDF 내보내기
            ("Ctrl+1", lambda: self.tabs.setCurrentIndex(0)),
            ("Ctrl+2", lambda: self.tabs.setCurrentIndex(1)),
            ("Ctrl+3", lambda: self.tabs.setCurrentIndex(2)),
            ("Ctrl+4", lambda: self.tabs.setCurrentIndex(3)),
        ]
        for seq, handler in shortcuts:
            action = QAction(self)
            action.setShortcut(QKeySequence(seq))
            action.triggered.connect(handler)
            self.addAction(action)

    def update_parameters_ui(self):
        """전략별 파라미터 UI 업데이트"""
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.param_inputs = {}
        strategy_name = self.strategy_combo.currentText()

        if "Momentum" in strategy_name:
            param_names = ["momentum_period", "mfi_level", "stop_loss"]
            default_values = [12, 46.5, 0.07]
            param_types = ["int", "float", "float"]

        elif "Trend" in strategy_name:
            param_names = ["short_window", "long_window", "stop_loss"]
            default_values = [12, 26, 0.07]
            param_types = ["int", "int", "float"]

        elif "Mean" in strategy_name:
            param_names = ["lookback_period", "z_score_threshold", "position_size"]
            default_values = [20, 1.96, 0.5]
            param_types = ["int", "float", "float"]

        else:
            param_names = ["portfolio_size", "correlation_filter", "momentum_period"]
            default_values = [5, 0.7, 12]
            param_types = ["int", "float", "int"]

        for param_name, default_val, param_type in zip(param_names, default_values, param_types):
            param_layout = QHBoxLayout()
            label = QLabel(param_name + ":")
            label.setFixedWidth(150)

            if param_type == "int":
                input_widget = QSpinBox()
                input_widget.setRange(1, 1000)
                input_widget.setValue(int(default_val))
            else:
                input_widget = QDoubleSpinBox()
                input_widget.setRange(0.001, 100)
                input_widget.setDecimals(3)
                input_widget.setValue(float(default_val))

            param_layout.addWidget(label)
            param_layout.addWidget(input_widget)
            param_layout.addStretch()

            self.params_layout.addLayout(param_layout)
            self.param_inputs[param_name] = input_widget

    def on_date_selection(self):
        """날짜 선택 다이얼로그"""
        dialog = DateRangeDialog(self)
        if dialog.exec():
            start_date, end_date = dialog.get_dates()
            self.state.start_date = start_date
            self.state.end_date = end_date
            self.date_display.setText(
                f"{start_date.toString('yyyy-MM-dd')} ~ {end_date.toString('yyyy-MM-dd')}"
            )

    def on_strategy_changed(self):
        """전략 변경 시 파라미터 UI 업데이트"""
        self.update_parameters_ui()

    def on_download_data(self):
        """데이터 다운로드"""
        ticker = self.ticker_input.text().upper().strip()
        valid, msg = InputValidator.validate_ticker(ticker)
        if not valid:
            QMessageBox.warning(self, "입력 오류", msg)
            return

        if not self.state.start_date or not self.state.end_date:
            QMessageBox.warning(self, "입력 오류", "날짜 범위를 선택하세요")
            return

        valid, msg = InputValidator.validate_date_range(self.state.start_date, self.state.end_date)
        if not valid:
            QMessageBox.warning(self, "입력 오류", msg)
            return

        self.state.stock_ticker = ticker
        self.status_label.setText(f"데이터 다운로드 중: {ticker}...")
        self.download_button.setEnabled(False)

        self.download_signals = DataDownloadSignals()
        self.download_signals.progress.connect(self.on_download_progress)
        self.download_signals.success.connect(self.on_download_success)
        self.download_signals.error.connect(self.on_download_error)

        downloader = DataDownloader()
        self.download_worker = DataDownloadWorker(
            downloader, ticker,
            self.state.start_date.toString('yyyy-MM-dd'),
            self.state.end_date.toString('yyyy-MM-dd'),
            self.download_signals
        )

        # 스레드를 인스턴스 속성으로 보관해 함수 종료 후 GC로 파괴되지 않도록 함
        self.download_thread = QThread()
        self.download_worker.moveToThread(self.download_thread)
        self.download_thread.started.connect(self.download_worker.run)
        self.download_worker.finished.connect(self.download_thread.quit)
        self.download_worker.finished.connect(self.download_worker.deleteLater)
        self.download_thread.finished.connect(self.download_thread.deleteLater)
        self.download_thread.start()

    def on_download_progress(self, message: str):
        """다운로드 진행 상황"""
        self.status_label.setText(message)

    def on_download_success(self, data: pd.DataFrame):
        """다운로드 성공"""
        self.state.stock_data = data
        self.status_label.setText(f"데이터 다운로드 완료: {len(data)} 행")
        self.download_button.setEnabled(True)
        self.tabs.setCurrentIndex(1)

    def on_download_error(self, error_message: str):
        """다운로드 오류"""
        QMessageBox.critical(self, "다운로드 오류", error_message)
        self.status_label.setText("준비 완료")
        self.download_button.setEnabled(True)

    def on_clear_cache(self):
        """캐시 삭제"""
        self.cache_manager.clear_all()
        self.cache_info.setText("캐시: 비어있음")
        QMessageBox.information(self, "캐시 삭제", "캐시가 모두 삭제되었습니다")

    def _create_strategy(self, strategy_name: str):
        """선택된 전략을 현재 설정(초기 자본/수수료)으로 생성."""
        capital = self.settings.get('initial_capital')
        fee = self.settings.get('transaction_fee')
        if "Momentum" in strategy_name:
            return MomentumStrategy(initial_capital=capital, transaction_fee=fee)
        elif "Trend" in strategy_name:
            return TrendFollowingStrategy(initial_capital=capital, transaction_fee=fee)
        elif "Mean" in strategy_name:
            return MeanReversionStrategy(initial_capital=capital, transaction_fee=fee)
        else:
            return PortfolioStrategy(initial_capital=capital, transaction_fee=fee)

    def on_run_backtest(self):
        """백테스트 실행"""
        if self.state.stock_data is None:
            QMessageBox.warning(self, "오류", "먼저 데이터를 다운로드하세요")
            return

        self.state.strategy_params = {
            param: input_widget.value()
            for param, input_widget in self.param_inputs.items()
        }

        strategy = self._create_strategy(self.strategy_combo.currentText())
        strategy.params = self.state.strategy_params

        try:
            self.status_label.setText("백테스트 실행 중...")
            result = self.engine.run_strategy(strategy, self.state.stock_data)
            self.state.backtest_results = result
            self.display_results(result)
            self.status_label.setText("백테스트 완료")
            self.tabs.setCurrentIndex(3)

        except Exception as e:
            QMessageBox.critical(self, "백테스트 오류", str(e))
            self.status_label.setText("준비 완료")

    def on_run_optimization(self):
        """최적화 실행"""
        if not self.optimization_checkbox.isChecked():
            QMessageBox.information(self, "최적화 미실행", "최적화를 활성화하세요")
            return

        if self.state.stock_data is None:
            QMessageBox.warning(self, "오류", "먼저 데이터를 다운로드하세요")
            return

        strategy = self._create_strategy(self.strategy_combo.currentText())

        try:
            self.status_label.setText("최적화 실행 중...")
            self.optimizer.use_parallel = self.parallel_checkbox.isChecked()

            param_ranges = self.state.optimization_settings
            if not param_ranges:
                QMessageBox.warning(self, "오류", "파라미터 범위를 설정하세요")
                return

            optimal_params, best_return, results = self.optimizer.optimize(
                strategy, self.state.stock_data, param_ranges
            )

            self.optimization_results.clear_results()
            for result in results[:10]:
                display_result = {k: v for k, v in result.items() if k != 'return'}
                self.optimization_results.add_result(
                    str(display_result),
                    {'cagr': result['return'], 'sharpe_ratio': 0, 'max_drawdown': 0,
                     'win_rate': 0, 'total_trades': 0, 'profit_loss_ratio': 0}
                )

            self.status_label.setText(f"최적화 완료: {best_return:.2%}")

        except Exception as e:
            QMessageBox.critical(self, "최적화 오류", str(e))
            self.status_label.setText("준비 완료")

    def on_set_ranges(self):
        """파라미터 범위 설정"""
        param_names = list(self.param_inputs.keys())
        dialog = ParameterRangeDialog(param_names, self)

        if dialog.exec():
            self.state.optimization_settings = dialog.get_ranges()
            self.ranges_display.setText("범위 설정 완료")

    def display_results(self, result: dict):
        """결과 표시"""
        metrics = result['metrics']

        self.metrics_table.setRowCount(0)
        metric_items = [
            ("CAGR", f"{metrics['cagr']:.2%}"),
            ("샤프 지수", f"{metrics['sharpe_ratio']:.2f}"),
            ("최대 낙폭", f"{metrics['max_drawdown']:.2%}"),
            ("칼마 비율", f"{metrics['calmar_ratio']:.2f}"),
            ("승률", f"{metrics['win_rate']:.2%}"),
            ("수익/손실 비율", f"{metrics['profit_loss_ratio']:.2f}"),
            ("총 거래", str(metrics['total_trades'])),
            ("수익 거래", str(metrics['winning_trades'])),
            ("손실 거래", str(metrics['losing_trades'])),
            ("평균 보유 기간", f"{metrics['avg_holding_period']:.1f}일"),
        ]

        for i, (metric_name, metric_value) in enumerate(metric_items):
            self.metrics_table.insertRow(i)
            self.metrics_table.setItem(i, 0, QTableWidgetItem(metric_name))
            self.metrics_table.setItem(i, 1, QTableWidgetItem(metric_value))

        report = self.engine.generate_report(result)
        self.report_text.setText(report)

    def on_show_chart_returns(self):
        """누적 수익률 차트 표시"""
        if not self.state.backtest_results:
            QMessageBox.warning(self, "오류", "백테스트를 먼저 실행하세요")
            return

        data = self.state.backtest_results['data']
        figure = plot_cumulative_returns(data, self.strategy_combo.currentText())
        dialog = ChartDialog(figure, "누적 수익률 차트", self)
        dialog.exec()

    def on_show_chart_indicators(self):
        """지표 차트 표시"""
        if not self.state.backtest_results:
            QMessageBox.warning(self, "오류", "백테스트를 먼저 실행하세요")
            return

        data = self.state.backtest_results['data']
        figure = plot_indicators(data, self.strategy_combo.currentText())
        dialog = ChartDialog(figure, "기술 지표 차트", self)
        dialog.exec()

    def on_show_chart_signals(self):
        """매매 신호 차트 표시"""
        if not self.state.backtest_results:
            QMessageBox.warning(self, "오류", "백테스트를 먼저 실행하세요")
            return

        data = self.state.backtest_results['data']
        figure = plot_buy_sell_signals(data, self.strategy_combo.currentText())
        dialog = ChartDialog(figure, "매매 신호 차트", self)
        dialog.exec()

    def on_export_csv(self):
        """CSV로 내보내기"""
        if not self.state.backtest_results:
            QMessageBox.warning(self, "오류", "백테스트를 먼저 실행하세요")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "CSV로 내보내기", "backtest_results.csv", "CSV 파일 (*.csv)"
        )
        if not path:
            return

        try:
            self.state.backtest_results['data'].to_csv(path, index=True)
            QMessageBox.information(self, "내보내기 완료", f"{path}로 저장되었습니다")
        except Exception as e:
            QMessageBox.critical(self, "내보내기 오류", str(e))

    def on_export_report(self):
        """보고서 저장"""
        if not self.state.backtest_results:
            QMessageBox.warning(self, "오류", "백테스트를 먼저 실행하세요")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "보고서 저장", "backtest_report.txt", "텍스트 파일 (*.txt)"
        )
        if not path:
            return

        try:
            report = self.engine.generate_report(self.state.backtest_results)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(report)
            QMessageBox.information(self, "저장 완료", f"{path}로 저장되었습니다")
        except Exception as e:
            QMessageBox.critical(self, "저장 오류", str(e))

    def on_export_pdf(self):
        """PDF 리포트로 내보내기 (지표 요약 + 차트)"""
        if not self.state.backtest_results:
            QMessageBox.warning(self, "오류", "백테스트를 먼저 실행하세요")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "PDF로 내보내기", "backtest_report.pdf", "PDF 파일 (*.pdf)"
        )
        if not path:
            return

        try:
            strategy_name = self.strategy_combo.currentText()
            export_backtest_pdf(self.state.backtest_results, path, strategy_name)
            QMessageBox.information(self, "내보내기 완료", f"{path}로 저장되었습니다")
        except Exception as e:
            QMessageBox.critical(self, "PDF 내보내기 오류", str(e))

    def on_settings(self):
        """설정 다이얼로그 표시 및 적용"""
        dialog = SettingsDialog(self.settings.all(), self)
        if dialog.exec():
            new_settings = dialog.get_settings()
            old_theme = self.settings.get('theme')
            for key, value in new_settings.items():
                self.settings.set(key, value)

            # 엔진/최적화기 재구성 및 테마 적용
            self._rebuild_engine_from_settings()
            if new_settings['theme'] != old_theme:
                apply_stylesheet(self, theme=new_settings['theme'])

            self.status_label.setText("설정이 저장되었습니다")

    def on_faq(self):
        """FAQ 다이얼로그 표시"""
        FAQDialog(self).exec()

    def on_about(self):
        """정보 표시"""
        QMessageBox.about(
            self,
            "QuantInvest Tool 정보",
            "QuantInvest Tool v1.0\n\n"
            "정량 투자 전략 분석 및 백테스팅 플랫폼\n\n"
            "개발: Development Team\n"
            "최종 업데이트: 2026-07-24"
        )
