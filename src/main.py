"""
QuantInvest Tool - Main Application Entry Point
"""

import os
import sys
import logging

# matplotlib의 Qt 백엔드가 PySide6 바인딩을 사용하도록 강제 (Qt 임포트 전에 설정)
os.environ.setdefault("QT_API", "PySide6")

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quantinvest.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """메인 애플리케이션 실행"""
    try:
        # PySide6 애플리케이션 생성
        app = QApplication(sys.argv)
        app.setApplicationName("QuantInvest Tool")
        app.setApplicationVersion("1.0.0")
        # QSettings 영속화를 위한 조직/앱 식별자
        app.setOrganizationName("QuantInvest")
        app.setOrganizationDomain("quantinvest.local")

        # 메인 윈도우 생성 및 표시
        window = MainWindow()
        window.show()

        logger.info("애플리케이션 시작됨")

        # 애플리케이션 실행
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"애플리케이션 오류: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
