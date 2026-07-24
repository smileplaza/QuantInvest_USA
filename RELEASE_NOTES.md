# 릴리스 노트

## v1.0.0 (2026-07-24) — MVP 릴리스

QuantInvest_Tool의 첫 정식 릴리스입니다. Jupyter 노트북 기반 교육용 퀀트 전략을 독립 실행형 GUI 애플리케이션으로 전환했습니다.

### ✨ 주요 기능

**4가지 트레이딩 전략**
- 모멘텀 전략 (가격 모멘텀 + MFI 필터)
- 추세 추종 전략 (EMA 크로스오버)
- 평균 회귀 전략 (Z-점수 기반)
- 포트폴리오 전략 (다종목 모멘텀)

**백테스팅 및 분석**
- 이벤트 기반 백테스팅 엔진
- 10개 성능 지표 (CAGR, 샤프, MDD, 칼마, 승률 등)
- 그리드 서치 파라미터 최적화 (병렬 처리 지원)
- SQLite 기반 데이터 캐싱

**사용자 인터페이스**
- PySide6 기반 4탭 GUI
- 다크/라이트 테마
- Matplotlib 차트 통합
- 스레드 안전 워커 (UI 응답성 유지)

### 🔧 기술 스택

- Python 3.12–3.14
- PySide6 (Qt 공식, LGPL v3)
- pandas, numpy, scipy, statsmodels, ta
- yfinance (주식 데이터)

### 🐛 수정된 버그

- 모멘텀 전략의 MFI 계산 파라미터 오류 수정 (`length` → `window`)
- SQLite 캐시 조회 시 컬럼명 손실 문제 수정 (pandas 3.0 호환)
- QThread 워커 생명주기 관리 개선 (GC로 인한 크래시 방지)

### ✅ 품질 검증

- 단위/통합 테스트 84개 전체 통과
- 핵심 로직 커버리지: metrics 96%, engine 84%, 전략 74-98%
- 4가지 전략 모두 엔드투엔드 워크플로 검증 완료

### 📦 배포

- Windows: `QuantInvest_Tool.exe` (단일 실행 파일)
- macOS/Linux: 소스 실행 또는 PyInstaller 빌드

### 📋 알려진 제한 사항

- PDF 보고서 생성 미지원 (향후 추가 예정)
- 실시간 데이터 피드 미지원
- 단일 종목 백테스트만 지원 (다종목 포트폴리오는 부분 지원)

---

전체 로드맵은 [.claude/knowledge/TO_DO.md](.claude/knowledge/TO_DO.md)를 참조하세요.
