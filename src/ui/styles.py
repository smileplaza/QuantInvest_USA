"""
PySide6 stylesheets for QuantInvest Tool
"""

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
    padding: 8px 20px;
    margin: 2px 2px 0px 0px;
    min-width: 100px;
    border: 1px solid #3d3d3d;
}

QTabBar::tab:selected {
    background-color: #0d47a1;
    color: #ffffff;
    border: 1px solid #0d47a1;
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

QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    padding: 5px;
    min-height: 28px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
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
    color: #ffffff;
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

QDialog {
    background-color: #1e1e1e;
    color: #ffffff;
}
"""

LIGHT_STYLESHEET = """
QMainWindow {
    background-color: #fafafa;
    color: #212121;
}

QWidget {
    background-color: #fafafa;
    color: #212121;
}

QTabBar::tab:selected {
    background-color: #1976d2;
    color: #ffffff;
}

QPushButton {
    background-color: #1976d2;
    color: #ffffff;
}

QPushButton:hover {
    background-color: #1565c0;
}
"""


def load_stylesheet(theme: str = "dark") -> str:
    """
    주어진 테마의 스타일시트 로드

    Args:
        theme (str): 테마 이름 ("dark" 또는 "light")

    Returns:
        str: 스타일시트 문자열
    """
    if theme == "light":
        return LIGHT_STYLESHEET
    else:
        return DARK_STYLESHEET


def apply_stylesheet(widget, theme: str = "dark"):
    """
    위젯에 스타일시트 적용

    Args:
        widget: PySide6 위젯
        theme (str): 테마 이름 ("dark" 또는 "light")
    """
    stylesheet = load_stylesheet(theme)
    widget.setStyleSheet(stylesheet)
