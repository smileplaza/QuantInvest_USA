"""
모달 다이얼로그 및 커스텀 위젯
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QCalendarWidget, QTableWidget, QTableWidgetItem, QProgressDialog,
    QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QMessageBox,
    QFormLayout, QTextBrowser, QDialogButtonBox
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd


class DateRangeDialog(QDialog):
    """날짜 범위 선택 다이얼로그"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("날짜 범위 선택")
        self.setGeometry(100, 100, 700, 400)

        self.start_date = None
        self.end_date = None

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # 시작 날짜
        start_layout = QVBoxLayout()
        start_label = QLabel("시작 날짜:")
        self.start_calendar = QCalendarWidget()
        self.start_calendar.setSelectedDate(QDate.currentDate().addYears(-2))
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_calendar)
        layout.addLayout(start_layout)

        # 종료 날짜
        end_layout = QVBoxLayout()
        end_label = QLabel("종료 날짜:")
        self.end_calendar = QCalendarWidget()
        self.end_calendar.setSelectedDate(QDate.currentDate())
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_calendar)
        layout.addLayout(end_layout)

        # 버튼
        button_layout = QVBoxLayout()
        ok_button = QPushButton("확인")
        cancel_button = QPushButton("취소")

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_dates(self):
        """선택된 날짜 반환"""
        return self.start_calendar.selectedDate(), self.end_calendar.selectedDate()


class ParameterRangeDialog(QDialog):
    """파라미터 범위 입력 다이얼로그"""

    def __init__(self, param_names: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("파라미터 범위 설정")
        self.setGeometry(100, 100, 500, 400)

        self.param_names = param_names
        self.ranges = {}
        self.inputs = {}

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 파라미터별 입력
        for param in self.param_names:
            param_layout = QHBoxLayout()

            label = QLabel(f"{param}:")
            min_spin = QSpinBox()
            max_spin = QSpinBox()
            step_spin = QSpinBox()

            min_spin.setRange(1, 1000)
            max_spin.setRange(1, 1000)
            step_spin.setRange(1, 100)

            min_spin.setValue(10)
            max_spin.setValue(50)
            step_spin.setValue(5)

            param_layout.addWidget(label)
            param_layout.addWidget(QLabel("최소:"))
            param_layout.addWidget(min_spin)
            param_layout.addWidget(QLabel("최대:"))
            param_layout.addWidget(max_spin)
            param_layout.addWidget(QLabel("단계:"))
            param_layout.addWidget(step_spin)

            self.inputs[param] = {
                'min': min_spin,
                'max': max_spin,
                'step': step_spin
            }

            layout.addLayout(param_layout)

        # 버튼
        button_layout = QHBoxLayout()
        ok_button = QPushButton("확인")
        cancel_button = QPushButton("취소")

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_ranges(self):
        """파라미터 범위 반환"""
        ranges = {}
        for param, inputs in self.inputs.items():
            min_val = inputs['min'].value()
            max_val = inputs['max'].value()
            step_val = inputs['step'].value()
            ranges[param] = (min_val, max_val, step_val)
        return ranges


class SettingsDialog(QDialog):
    """애플리케이션 설정 다이얼로그.

    테마, 초기 자본, 거래 수수료, 무위험 이율, 병렬 처리 기본값을 편집한다.
    현재 값을 dict로 받아 표시하고, get_settings()로 편집 결과를 반환한다.
    """

    def __init__(self, current: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("설정")
        self.setMinimumWidth(420)
        self._build_ui(current)

    def _build_ui(self, current: dict):
        layout = QVBoxLayout()
        form = QFormLayout()

        # 테마
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(current.get('theme', 'dark'))
        self.theme_combo.setToolTip("애플리케이션 색상 테마 (다크/라이트)")
        form.addRow("테마:", self.theme_combo)

        # 초기 자본
        self.capital_spin = QDoubleSpinBox()
        self.capital_spin.setRange(100.0, 1_000_000_000.0)
        self.capital_spin.setDecimals(2)
        self.capital_spin.setSingleStep(1000.0)
        self.capital_spin.setValue(current.get('initial_capital', 10000.0))
        self.capital_spin.setToolTip("백테스트 시작 자본금 (통화 단위)")
        form.addRow("초기 자본:", self.capital_spin)

        # 거래 수수료
        self.fee_spin = QDoubleSpinBox()
        self.fee_spin.setRange(0.0, 0.1)
        self.fee_spin.setDecimals(4)
        self.fee_spin.setSingleStep(0.0005)
        self.fee_spin.setValue(current.get('transaction_fee', 0.001))
        self.fee_spin.setToolTip("1회 거래당 수수료율 (예: 0.001 = 0.1%)")
        form.addRow("거래 수수료율:", self.fee_spin)

        # 무위험 이율
        self.rfr_spin = QDoubleSpinBox()
        self.rfr_spin.setRange(0.0, 0.2)
        self.rfr_spin.setDecimals(4)
        self.rfr_spin.setSingleStep(0.001)
        self.rfr_spin.setValue(current.get('risk_free_rate', 0.003))
        self.rfr_spin.setToolTip("샤프 지수 계산에 사용하는 연 무위험 이율")
        form.addRow("무위험 이율:", self.rfr_spin)

        # 병렬 처리
        self.parallel_check = QCheckBox("최적화 시 병렬 처리 기본 사용")
        self.parallel_check.setChecked(current.get('use_parallel', False))
        self.parallel_check.setToolTip("그리드 서치를 여러 CPU 코어로 분산 실행")
        form.addRow("병렬 처리:", self.parallel_check)

        layout.addLayout(form)

        # 표준 버튼 (확인/취소/기본값 복원)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self._restore_defaults)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def _restore_defaults(self):
        """입력 필드를 기본값으로 되돌림 (저장은 확인 시)."""
        self.theme_combo.setCurrentText('dark')
        self.capital_spin.setValue(10000.0)
        self.fee_spin.setValue(0.001)
        self.rfr_spin.setValue(0.003)
        self.parallel_check.setChecked(False)

    def get_settings(self) -> dict:
        """편집된 설정을 dict로 반환."""
        return {
            'theme': self.theme_combo.currentText(),
            'initial_capital': self.capital_spin.value(),
            'transaction_fee': self.fee_spin.value(),
            'risk_free_rate': self.rfr_spin.value(),
            'use_parallel': self.parallel_check.isChecked(),
        }


class FAQDialog(QDialog):
    """자주 묻는 질문(FAQ) 표시 다이얼로그."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("자주 묻는 질문 (FAQ)")
        self.setMinimumSize(640, 520)

        layout = QVBoxLayout()
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._faq_html())
        layout.addWidget(browser)

        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_button)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    @staticmethod
    def _faq_html() -> str:
        return """
        <h2>QuantInvest Tool 자주 묻는 질문</h2>

        <h3>Q. 데이터 다운로드가 실패합니다.</h3>
        <p>인터넷 연결, 티커 심볼(예: AAPL), 날짜 범위를 확인하세요.
        Yahoo Finance에서 해당 종목/기간 데이터를 제공하지 않을 수 있습니다.
        시작 날짜가 종료 날짜보다 앞서야 합니다.</p>

        <h3>Q. "데이터가 부족합니다" 오류가 납니다.</h3>
        <p>전략 파라미터(기간)가 다운로드한 데이터 길이보다 큰 경우입니다.
        예를 들어 60일 데이터에 100일 이동평균은 계산할 수 없습니다.
        파라미터를 줄이거나 더 긴 날짜 범위를 선택하세요.</p>

        <h3>Q. 최적화가 너무 오래 걸립니다.</h3>
        <p>그리드 서치는 조합 수에 비례해 느려집니다. 파라미터 범위를 좁히거나
        단계(step)를 키우세요. 설정에서 <b>병렬 처리</b>를 켜면 여러 CPU
        코어로 분산되어 빨라집니다.</p>

        <h3>Q. 4개 전략은 어떻게 다른가요?</h3>
        <ul>
          <li><b>모멘텀</b>: 가격 상승 추세 + 자금 흐름 지수(MFI) 필터</li>
          <li><b>추세 추종</b>: 단기/장기 지수이동평균(EMA) 교차</li>
          <li><b>평균 회귀</b>: Z-점수 기반 통계적 반전</li>
          <li><b>포트폴리오</b>: 다종목 모멘텀 프록시</li>
        </ul>

        <h3>Q. 결과가 원본 교재(노트북)와 다릅니다.</h3>
        <p>추세 추종 전략은 원본 노트북과 0.1% 이내로 일치합니다. 모멘텀 전략은
        MFI 필터가 추가된 확장 구현이며, 평균 회귀/포트폴리오는 단일 종목용으로
        단순화된 버전입니다. 자세한 내용은 NOTEBOOK_VALIDATION.md를 참고하세요.</p>

        <h3>Q. 결과를 어떻게 저장하나요?</h3>
        <p>결과 분석 탭에서 <b>CSV로 내보내기</b>, <b>보고서 저장</b>,
        <b>PDF로 내보내기</b>를 사용할 수 있습니다. 차트 창에서는 개별
        이미지(PNG) 저장도 가능합니다.</p>

        <h3>Q. 단축키가 있나요?</h3>
        <p>Ctrl+D 다운로드, Ctrl+R 백테스트, Ctrl+Shift+O 최적화,
        Ctrl+E CSV 내보내기, Ctrl+P PDF 내보내기, Ctrl+, 설정,
        Ctrl+1~4 탭 이동, F1 이 도움말, Ctrl+Q 종료.</p>
        """


class ChartDialog(QDialog):
    """차트 표시 다이얼로그"""

    def __init__(self, figure: Figure, title: str = "차트", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 1000, 600)

        layout = QVBoxLayout()

        # 차트 캔버스
        self.canvas = FigureCanvas(figure)
        layout.addWidget(self.canvas)

        # 버튼
        button_layout = QHBoxLayout()
        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.accept)

        save_button = QPushButton("저장")
        save_button.clicked.connect(self.save_chart)

        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.figure = figure

    def save_chart(self):
        """차트를 이미지로 저장"""
        try:
            self.figure.savefig('chart.png', dpi=300, bbox_inches='tight')
            QMessageBox.information(self, "저장 완료", "차트가 저장되었습니다: chart.png")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"저장 실패: {str(e)}")


class ProgressDialog(QProgressDialog):
    """진행 상황 표시 다이얼로그"""

    def __init__(self, title: str = "처리 중...", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setRange(0, 100)
        self.setMinimumWidth(400)
        self.setModal(True)
        self.setAutoClose(True)
        self.setAutoReset(True)

    def update_progress(self, current: int, total: int):
        """진행 상황 업데이트"""
        percentage = int((current / total) * 100) if total > 0 else 0
        self.setValue(percentage)
        self.setLabelText(f"진행: {current}/{total}")


class ResultsTableWidget(QTableWidget):
    """결과 테이블 위젯"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "전략",
            "CAGR",
            "샤프 지수",
            "최대 낙폭",
            "승률",
            "총 거래",
            "P/L 비율"
        ])
        self.resizeColumnsToContents()

    def add_result(self, strategy_name: str, metrics: dict):
        """결과 추가"""
        row = self.rowCount()
        self.insertRow(row)

        items = [
            strategy_name,
            f"{metrics.get('cagr', 0):.2%}",
            f"{metrics.get('sharpe_ratio', 0):.2f}",
            f"{metrics.get('max_drawdown', 0):.2%}",
            f"{metrics.get('win_rate', 0):.2%}",
            str(metrics.get('total_trades', 0)),
            f"{metrics.get('profit_loss_ratio', 0):.2f}"
        ]

        for col, item_text in enumerate(items):
            item = QTableWidgetItem(item_text)
            item.setFont(QFont("Arial", 10))
            self.setItem(row, col, item)

        self.resizeColumnsToContents()

    def clear_results(self):
        """테이블 초기화"""
        self.setRowCount(0)
