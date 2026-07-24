"""
PDF 리포트 생성 및 설정(AppSettings) 테스트

UI 다이얼로그 자체는 오프스크린 스모크만 하고, 핵심 로직(PDF 생성,
설정 형변환/영속화)은 헤드리스로 검증한다.
"""

import os

import numpy as np
import pandas as pd
import pytest

from strategies.trend_following import TrendFollowingStrategy
from backtest.engine import BacktestEngine
from utils.report import export_backtest_pdf


@pytest.fixture
def backtest_result(sample_data):
    strat = TrendFollowingStrategy()
    engine = BacktestEngine()
    return engine.run_strategy(strat, sample_data)


class TestPdfExport:
    """PDF 리포트 생성"""

    def test_creates_valid_pdf_file(self, backtest_result, tmp_path):
        out = tmp_path / "report.pdf"
        result_path = export_backtest_pdf(backtest_result, str(out), "Trend Following")

        assert os.path.exists(result_path)
        assert os.path.getsize(result_path) > 0
        # PDF 매직 넘버 확인
        with open(result_path, "rb") as f:
            assert f.read(5) == b"%PDF-"

    def test_invalid_result_raises(self, tmp_path):
        out = tmp_path / "bad.pdf"
        with pytest.raises(ValueError):
            export_backtest_pdf({}, str(out))

    def test_missing_data_key_raises(self, tmp_path):
        out = tmp_path / "bad.pdf"
        with pytest.raises(ValueError):
            export_backtest_pdf({'metrics': {}}, str(out))


class TestAppSettings:
    """설정 형변환 및 기본값 (QSettings는 임시 조직명으로 격리)"""

    @pytest.fixture(autouse=True)
    def _isolated_qsettings(self, tmp_path, monkeypatch):
        # QSettings가 실제 사용자 설정을 건드리지 않도록 격리
        from PySide6.QtCore import QSettings, QCoreApplication
        QCoreApplication.setOrganizationName("QuantInvestTest")
        QCoreApplication.setApplicationName("QuantInvestToolTest")
        QSettings.setPath(
            QSettings.IniFormat, QSettings.UserScope, str(tmp_path)
        )
        QSettings.setDefaultFormat(QSettings.IniFormat)
        yield

    def test_defaults(self):
        from ui.utils.settings import AppSettings
        s = AppSettings()
        s.reset()
        assert s.get('theme') == 'dark'
        assert s.get('initial_capital') == pytest.approx(10000.0)
        assert s.get('transaction_fee') == pytest.approx(0.001)
        assert s.get('use_parallel') is False

    def test_set_and_get_roundtrip(self):
        from ui.utils.settings import AppSettings
        s = AppSettings()
        s.set('initial_capital', 50000.0)
        s.set('theme', 'light')
        s.set('use_parallel', True)

        s2 = AppSettings()  # 새 인스턴스로 영속화 확인
        assert s2.get('initial_capital') == pytest.approx(50000.0)
        assert s2.get('theme') == 'light'
        assert s2.get('use_parallel') is True

    def test_unknown_key_raises(self):
        from ui.utils.settings import AppSettings
        s = AppSettings()
        with pytest.raises(KeyError):
            s.get('nonexistent')
        with pytest.raises(KeyError):
            s.set('nonexistent', 1)

    def test_bool_cast_from_string(self):
        from ui.utils.settings import AppSettings
        from PySide6.QtCore import QSettings
        QSettings().setValue('use_parallel', 'true')
        s = AppSettings()
        assert s.get('use_parallel') is True

    def test_all_returns_full_dict(self):
        from ui.utils.settings import AppSettings
        s = AppSettings()
        data = s.all()
        assert set(data.keys()) == {
            'theme', 'initial_capital', 'transaction_fee',
            'risk_free_rate', 'use_parallel'
        }
