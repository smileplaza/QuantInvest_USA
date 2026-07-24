# QuantInvest_Tool

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green)](https://wiki.qt.io/Qt_for_Python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

정량적(퀀트) 트레이딩 전략을 분석하고 백테스팅하기 위한 전문적인 GUI 애플리케이션입니다. Jupyter 노트북의 교육용 전략을 독립 실행형 .exe 도구로 변환했습니다.

## 📋 목차

- [주요 기능](#주요-기능)
- [설치](#설치)
- [빠른 시작](#빠른-시작)
- [기능 상세](#기능-상세)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [문서](#문서)
- [문제 해결](#문제-해결)
- [라이선스](#라이선스)

## ✨ 주요 기능

### 🎯 4가지 트레이딩 전략
- **모멘텀 전략** — 가격 모멘텀 + 자금 흐름 지수(MFI) 필터
- **추세 추종 전략** — 지수 이동 평균(EMA) 교차
- **평균 회귀 전략** — Z-점수 기반 통계적 반전 거래
- **포트폴리오 전략** — 다종목 모멘텀 + 상관관계 분석

### 📊 포괄적인 분석
- **실시간 백테스팅** — 과거 데이터 기반 전략 성과 검증
- **파라미터 최적화** — 그리드 서치를 통한 최적 매개변수 자동 탐색
- **성능 지표** — CAGR, 샤프 비율, 최대 낙폭, 승률 등 10개 이상 지표
- **시각화** — 누적 수익률, 기술 지표, 매매 신호 차트

### 💾 효율적인 데이터 관리
- **SQLite 캐싱** — yfinance 중복 다운로드 방지, 로컬 저장
- **빠른 데이터 로드** — 캐시된 데이터 즉시 사용
- **유연한 날짜 범위** — 1일 ~ 30년의 데이터 분석 가능

## 🚀 설치

### 사전 요구 사항
- **Python 3.12** 이상 (3.12–3.14 검증됨)
- **Windows** (PyInstaller .exe 생성용)
- pip 패키지 관리자

### 단계별 설치

**1. 저장소 클론**
```bash
git clone https://github.com/smileplaza/QuantInvest_USA.git
cd QuantInvest_USA
```

**2. 가상 환경 생성**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**3. 의존성 설치**
```bash
pip install -r requirements.txt
```

### 선택 사항: 개발 환경

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

## 🎮 빠른 시작

### 애플리케이션 실행

```bash
python src/main.py
```

GUI가 열리면:

1. **탭 1: 주식 및 날짜 설정**
   - 티커 입력 (예: AAPL, MSFT)
   - 날짜 범위 선택
   - "데이터 다운로드" 클릭

2. **탭 2: 전략 선택 및 파라미터**
   - 4개 전략 중 선택
   - 파라미터 설정
   - "백테스트 실행" 클릭

3. **탭 3: 최적화 설정** (선택)
   - 파라미터 범위 정의
   - 최적화 활성화
   - "최적화 시작" 클릭

4. **탭 4: 결과 분석**
   - 성능 지표 표시
   - 차트 생성 및 내보내기
   - CSV / 텍스트 보고서 / **PDF 리포트** 저장

> 💡 **설정** (`Ctrl+,`)에서 초기 자본, 거래 수수료, 무위험 이율, 테마(다크/라이트),
> 병렬 처리 기본값을 변경할 수 있습니다. **단축키**: `Ctrl+D` 다운로드,
> `Ctrl+R` 백테스트, `Ctrl+Shift+O` 최적화, `Ctrl+E` CSV, `Ctrl+P` PDF,
> `Ctrl+1~4` 탭 이동, `F1` 도움말(FAQ).

## 🔧 기능 상세

### 백테스팅 엔진
- **이벤트 기반 시뮬레이션** — 실제 거래 순서대로 처리
- **포지션 관리** — 현금, 보유 자산, 거래 이력 추적
- **리스크 관리** — 트레일링 스톱 로스, 거래 수수료 모델링

### 성능 지표 (10개)
| 지표 | 설명 |
|------|------|
| CAGR | 연평균 복리 성장률 |
| 샤프 비율 | 위험 조정 수익률 |
| 최대 낙폭 | 최악의 고점 대비 저점 하락 |
| 칼마 비율 | 낙폭 단위당 수익 |
| 승률 | 수익성 있는 거래의 비율 |
| 손익비 | 평균 이익 대 평균 손실 |
| 총 거래 | 완료된 거래 수 |
| 평균 보유 기간 | 평균 보유 기간(영업일) |

### 파라미터 최적화
- **그리드 서치** — 파라미터 공간의 모든 조합 평가
- **병렬 처리** — 선택적으로 여러 CPU 코어 활용
- **실시간 진행** — 진행률 표시 및 최적 파라미터 추적

## 🏗️ 기술 스택

### 핵심 의존성
| 라이브러리 | 버전 | 용도 |
|----------|------|------|
| PySide6 | >=6.11,<7 | GUI 프레임워크 (Qt 공식) |
| pandas | >=3.0,<4 | 데이터 조작 |
| numpy | >=2.3,<3 | 수치 계산 |
| yfinance | >=1.5.2,<2 | 주식 데이터 다운로드 |
| scipy | >=1.16,<2 | 과학 계산 |
| statsmodels | >=0.14.5 | 통계 분석 |
| matplotlib | >=3.10.5 | 데이터 시각화 |
| ta | >=0.11,<1 | 기술 지표 |

### 개발 도구
| 도구 | 버전 | 용도 |
|-----|------|------|
| pytest | >=8.0,<10 | 단위 테스트 |
| black | >=25.0,<27 | 코드 포매팅 |
| flake8 | >=7.3,<8 | 코드 린팅 |
| isort | >=6.0,<9 | 임포트 정렬 |
| PyInstaller | >=6.16,<7 | .exe 패키징 |

## 📁 프로젝트 구조

```
QuantInvest_USA/
├── src/                           # 메인 애플리케이션 소스
│   ├── main.py                    # 애플리케이션 진입점
│   ├── ui/                        # PySide6 사용자 인터페이스
│   │   ├── main_window.py         # 메인 창 (4개 탭)
│   │   ├── dialogs.py             # 모달 대화 상자 및 차트
│   │   └── styles.py              # 다크/라이트 테마
│   ├── strategies/                # 4가지 트레이딩 전략
│   │   ├── base_strategy.py       # 추상 기본 클래스
│   │   ├── momentum_strategy.py    # 모멘텀
│   │   ├── trend_following.py      # 추세 추종
│   │   ├── mean_reversion.py       # 평균 회귀
│   │   └── portfolio.py            # 포트폴리오
│   ├── backtest/                  # 백테스팅 엔진
│   │   ├── engine.py              # 메인 백테스트 루프
│   │   ├── metrics.py             # 성능 지표 계산
│   │   └── optimizer.py           # 파라미터 최적화
│   ├── data/                      # 데이터 관리
│   │   ├── downloader.py          # yfinance 래퍼
│   │   └── cache.py               # SQLite 캐시
│   └── utils/                     # 유틸리티
│       ├── plotting.py            # Matplotlib 차트
│       └── formatting.py          # 데이터 포매팅
├── tests/                         # 단위 테스트
├── samples/                       # 원본 Jupyter 노트북
├── requirements.txt               # 런타임 의존성
├── requirements-dev.txt           # 개발 의존성
├── pyproject.toml                 # 프로젝트 설정
├── setup.py                       # 패키지 설정
├── CLAUDE.md                      # 개발 가이드
├── ARCHITECTURE.md                # 시스템 아키텍처
└── README.md                      # 이 파일
```

## 📚 문서

- **[CLAUDE.md](CLAUDE.md)** — 개발 환경 설정 및 코드 구조
- **[FAQ.md](FAQ.md)** — 자주 묻는 질문
- **[.claude/knowledge/ARCHITECTURE.md](.claude/knowledge/ARCHITECTURE.md)** — 시스템 아키텍처 및 데이터 흐름
- **[.claude/knowledge/TO_DO.md](.claude/knowledge/TO_DO.md)** — 기능 로드맵 및 개발 진행
- **[.claude/knowledge/NOTEBOOK_VALIDATION.md](.claude/knowledge/NOTEBOOK_VALIDATION.md)** — 노트북 대비 검증 리포트

## 🧪 테스트

### 단위 테스트 실행
```bash
pytest tests/ -v
```

### 커버리지 리포트
```bash
pytest tests/ --cov=src
```

### 전략 검증 (빠른 스모크 테스트)
```bash
python -c "
import pandas as pd
import numpy as np
from src.strategies.trend_following import TrendFollowingStrategy
from src.backtest.engine import BacktestEngine

# 합성 데이터 생성
n = 300
idx = pd.date_range('2022-01-01', periods=n, freq='B')
price = 100 + np.cumsum(np.random.normal(0, 1, n))
df = pd.DataFrame({'Open': price*0.99, 'High': price*1.02, 
                   'Low': price*0.98, 'Close': price, 
                   'Volume': np.random.randint(1e6, 5e6, n)}, index=idx)

# 백테스트 실행
engine = BacktestEngine()
result = engine.run_strategy(TrendFollowingStrategy(), df)
print(f'CAGR: {result[\"metrics\"][\"cagr\"]:.2%}')
"
```

## ⚠️ 문제 해결

### yfinance 데이터 다운로드 오류

**문제**: "No data found" 또는 "multi_level_index" 오류

**해결책**:
1. yfinance 업그레이드
   ```bash
   pip install --upgrade yfinance
   ```

2. 이미 최신 버전을 설치했다면, 코드에서 사용하는 download() 호출이 다음 옵션을 포함하는지 확인합니다:
   ```python
   yf.download(ticker, start, end, multi_level_index=False, auto_adjust=False)
   ```

> **참고**: 2025년 2월 20일부로 Yahoo Finance 데이터 형식이 변경되었습니다. QuantInvest_Tool은 이미 최신 형식을 지원합니다.

### PyInstaller .exe 생성 오류

**문제**: "Failed to create executable"

**해결책**:
```bash
# 모든 캐시 정리
pyinstaller --clean --onefile --windowed --name "QuantInvest_Tool" src/main.py
```

### PySide6 import 오류

**문제**: "ModuleNotFoundError: No module named 'PySide6'"

**해결책**:
```bash
pip install --upgrade PySide6
```

## 📈 사용 사례

### 개인 투자자
- 관심 종목의 다양한 전략 테스트
- 최적 파라미터 자동 탐색
- 성과 비교 및 선택

### 금융 학생
- 퀀트 투자 개념 실습
- 실제 시장 데이터로 검증
- 기술 지표 학습

### 트레이딩 개발자
- 새로운 전략 빠른 프로토타입
- 파라미터 민감도 분석
- 상용 시스템으로 확장 기반

## 🔮 향후 계획

- [ ] 추가 기술 지표 (RSI, MACD, Bollinger Bands)
- [ ] 다중 종목 포트폴리오 분석
- [ ] 실시간 데이터 피드 (WebSocket)
- [ ] 옵션 전략 분석
- [ ] 국제 시장 확대 (한국, 일본, 홍콩)
- [ ] 클라우드 백테스트 서비스
- [ ] 알고리즘 트레이딩 연동

자세한 로드맵은 [TO_DO.md](TO_DO.md)를 참조하세요.

## 📄 라이선스

MIT License — 자유롭게 사용, 수정, 배포 가능합니다.
[LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여

이슈, 기능 요청, Pull Request를 환영합니다!

1. 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치를 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 📞 문의 및 지원

- **이슈 신고**: [GitHub Issues](https://github.com/smileplaza/QuantInvest_USA/issues)
- **이메일**: sahong@kakao.com
- **문서**: 이 저장소의 [설명서](ARCHITECTURE.md) 및 [개발 가이드](CLAUDE.md) 참조

## 🙏 감사의 말

- 원본 교재: 대표전략으로 입문하는 미국주식 퀀트투자
- 데이터 출처: Yahoo Finance (yfinance)
- GUI 프레임워크: PySide6 (Qt for Python)

---

**QuantInvest_Tool** — 누구나 사용할 수 있는 전문적인 퀀트 분석 도구

**최종 업데이트**: 2026년 7월 24일 | **버전**: 1.0.0
