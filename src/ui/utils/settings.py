"""
애플리케이션 설정 영속화 (QSettings 래퍼)

테마, 초기 자본, 거래 수수료, 무위험 이율, 병렬 처리 기본값 등을
플랫폼별 표준 위치(레지스트리/plist/ini)에 저장하고 불러온다.
"""

from PySide6.QtCore import QSettings


class AppSettings:
    """타입 안전한 기본값과 접근자를 제공하는 설정 관리자."""

    # (키, 기본값, 형변환 함수)
    _DEFAULTS = {
        'theme': ('dark', str),
        'initial_capital': (10000.0, float),
        'transaction_fee': (0.001, float),
        'risk_free_rate': (0.003, float),
        'use_parallel': (False, bool),
    }

    def __init__(self):
        # 조직/앱 이름은 QApplication에서 설정됨 (main.py)
        self._settings = QSettings()

    def _cast_bool(self, value) -> bool:
        # QSettings는 bool을 문자열('true'/'false')로 저장할 수 있음
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', '1', 'yes')

    def get(self, key: str):
        """키에 해당하는 설정값을 기본값/형변환과 함께 반환."""
        if key not in self._DEFAULTS:
            raise KeyError(f"알 수 없는 설정 키: {key}")
        default, caster = self._DEFAULTS[key]
        raw = self._settings.value(key, default)
        if caster is bool:
            return self._cast_bool(raw)
        try:
            return caster(raw)
        except (TypeError, ValueError):
            return default

    def set(self, key: str, value) -> None:
        """설정값 저장 (즉시 플러시)."""
        if key not in self._DEFAULTS:
            raise KeyError(f"알 수 없는 설정 키: {key}")
        self._settings.setValue(key, value)
        self._settings.sync()

    def all(self) -> dict:
        """모든 설정을 dict로 반환."""
        return {key: self.get(key) for key in self._DEFAULTS}

    def reset(self) -> None:
        """모든 설정을 기본값으로 초기화."""
        for key in self._DEFAULTS:
            self._settings.remove(key)
        self._settings.sync()
