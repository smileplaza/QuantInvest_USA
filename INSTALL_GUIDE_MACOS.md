# QuantInvest_Tool — macOS 설치 및 컴파일 가이드

![macOS](https://img.shields.io/badge/Platform-macOS%2011%2B-000000?logo=apple)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776ab?logo=python)
![Status](https://img.shields.io/badge/Status-Production-28a745)

macOS에서 QuantInvest_Tool을 설치하고 실행하는 완전한 가이드입니다.

> **참고**: PyInstaller 기반 .exe 생성은 Windows 전용입니다. macOS에서는 소스 코드로 실행하거나, 선택적으로 .app 번들을 생성할 수 있습니다.

## 📋 목차

- [시스템 요구사항](#시스템-요구사항)
- [사전 설치](#사전-설치)
- [단계별 설치](#단계별-설치)
- [애플리케이션 실행](#애플리케이션-실행)
- [macOS App Bundle 생성 (선택)](#macos-app-bundle-생성-선택)
- [문제 해결](#문제-해결)

---

## 🖥️ 시스템 요구사항

### 최소 사양
- **OS**: macOS 11 (Big Sur) 이상
- **Python**: 3.12 ~ 3.14
- **RAM**: 4GB 이상
- **디스크**: 2GB (가상 환경 + 의존성)
- **프로세서**: Intel 또는 Apple Silicon (M1/M2/M3)
- **인터넷**: 초기 설치 시 필수

### 확인 방법

```bash
# macOS 버전 확인
sw_vers

# 설치된 Python 확인
python3 --version

# 프로세서 확인 (Apple Silicon인 경우 "Apple" 포함)
uname -m
```

---

## 📦 사전 설치

### 1. Homebrew 설치 (권장)

```bash
# Homebrew 설치 (macOS 패키지 관리자)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# M1/M2/M3 (Apple Silicon) 사용자:
# 설치 후 다음 명령 실행
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# 설치 확인
brew --version
```

### 2. Python 3.12+ 설치

**방법 1: Homebrew (권장)**
```bash
# Python 설치
brew install python@3.12

# 심볼릭 링크 생성 (python3 명령어 사용)
brew link python@3.12

# 설치 확인
python3 --version
```

**방법 2: python.org에서 설치**
1. https://www.python.org/downloads/ 방문
2. "Download Python 3.12" 클릭
3. macOS 인스톨러 실행 (Intel/Apple Silicon 자동 감지)

**설치 확인**
```bash
python3 --version
python3 -m pip --version
```

### 3. Git 설치 (저장소 클론용)

```bash
# Homebrew로 설치
brew install git

# 설치 확인
git --version
```

### 4. Xcode Command Line Tools (선택, 일부 패키지 빌드용)

```bash
# 자동으로 필요시 설치됨
# 수동 설치:
xcode-select --install
```

---

## 🚀 단계별 설치

### Step 1: 저장소 클론

```bash
# 작업 디렉터리 이동 (예: ~/Projects)
cd ~/Projects

# 저장소 클론
git clone https://github.com/smileplaza/QuantInvest_USA.git
cd QuantInvest_USA
```

### Step 2: 가상 환경 생성 및 활성화

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# 성공 확인 (프롬프트에 (venv) 표시)
# (venv) user@macbook QuantInvest_USA %
```

### Step 3: 패키지 업그레이드

```bash
# pip 최신 버전으로 업데이트
python -m pip install --upgrade pip setuptools wheel
```

### Step 4: 의존성 설치

```bash
# 런타임 의존성 설치
pip install -r requirements.txt

# 설치 확인
pip list | grep -E "PySide6|pandas|numpy|yfinance"
```

> **Apple Silicon 사용자 참고**: numpy, scipy, pandas는 자동으로 arm64 버전을 설치합니다.

### Step 5: 애플리케이션 실행 테스트

```bash
# 애플리케이션 실행
python src/main.py
```

✓ GUI 창이 열리면 설치 성공!

---

## 🎮 애플리케이션 실행

### 일반 실행

```bash
# 가상 환경 활성화 필수
source venv/bin/activate

# 애플리케이션 실행
python src/main.py
```

### 백그라운드 실행

```bash
# nohup으로 백그라운드 실행 (터미널 종료 후에도 계속 실행)
nohup python src/main.py > /dev/null 2>&1 &
```

### 편리한 스크립트 생성

`run.sh` 파일 생성:

```bash
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python src/main.py
```

실행 권한 추가:
```bash
chmod +x run.sh

# 실행
./run.sh
```

### Finder에서 더블클릭으로 실행

`run_app.command` 파일 생성:

```bash
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python src/main.py
```

권한 추가 및 실행:
```bash
chmod +x run_app.command

# Finder에서 더블클릭
```

---

## 📦 macOS App Bundle 생성 (선택)

### Step 1: 필요한 도구 설치

```bash
# 가상 환경 활성화
source venv/bin/activate

# PyInstaller 또는 pyapp 설치
pip install pyinstaller>=6.16

# macOS 전용 도구
pip install py2app
```

### Step 2: py2app을 사용한 .app 생성

먼저 `setup.py` 업데이트:

```python
from setuptools import setup

APP = ['src/main.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PySide6', 'pandas', 'numpy', 'yfinance', 'ta', 'scipy', 'statsmodels', 'matplotlib'],
    'includes': ['PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui'],
}

setup(
    app=APP,
    name='QuantInvest_Tool',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

그 후:

```bash
# .app 번들 생성
python setup.py py2app

# 또는 간단한 방식 (권장)
py2app
```

### Step 3: 생성된 앱 확인

```bash
# Applications 폴더에 복사
cp -r dist/QuantInvest\ Tool.app ~/Applications/

# Finder에서 실행
open ~/Applications/QuantInvest\ Tool.app
```

### Step 4: DMG 배포 이미지 생성 (선택)

```bash
# DMG 생성
hdiutil create -volname "QuantInvest_Tool" \
  -srcfolder dist \
  -ov -format UDZO "QuantInvest_Tool_v1.0.0.dmg"
```

---

## 🔧 PyInstaller를 사용한 단일 실행 파일 생성

### Step 1: PyInstaller 설치

```bash
# 가상 환경 활성화 필수
source venv/bin/activate

# PyInstaller 설치
pip install pyinstaller>=6.16,<7
```

### Step 2: 빌드

```bash
# macOS용 단일 실행 파일 생성
pyinstaller --clean --onefile --windowed \
  --name "QuantInvest_Tool" \
  --osx-bundle-identifier="com.quantinvest.tool" \
  src/main.py
```

### Step 3: 결과 확인

```bash
# 생성된 파일 확인
ls -lh dist/

# 예상 출력:
# QuantInvest_Tool (실행 파일, 150-200 MB)
```

### Step 4: 실행 테스트

```bash
# 실행
./dist/QuantInvest\ Tool
```

---

## 🧪 테스트

### 단위 테스트 실행

```bash
# 가상 환경 활성화 필수
source venv/bin/activate

# 테스트 실행
pytest tests/ -v

# 커버리지 리포트
pytest tests/ --cov=src --cov-report=html

# 브라우저에서 확인
open htmlcov/index.html
```

### 애플리케이션 스모크 테스트

```bash
# 빠른 검증 (합성 데이터)
python3 << 'EOF'
import pandas as pd
import numpy as np
from src.strategies.trend_following import TrendFollowingStrategy
from src.backtest.engine import BacktestEngine

n = 300
idx = pd.date_range('2022-01-01', periods=n, freq='B')
price = 100 + np.cumsum(np.random.normal(0, 1, n))
df = pd.DataFrame({
    'Open': price*0.99, 'High': price*1.02, 'Low': price*0.98,
    'Close': price, 'Volume': np.random.randint(1000000, 5000000, n)
}, index=idx)

engine = BacktestEngine()
result = engine.run_strategy(TrendFollowingStrategy(), df)
print(f'✓ 백테스트 성공: CAGR {result["metrics"]["cagr"]:.2%}')
EOF
```

---

## ⚠️ 문제 해결

### 문제 1: Python이 설치되지 않았음

```
python3: command not found
```

**해결책**:
```bash
# Homebrew로 설치
brew install python@3.12

# 또는 python.org에서 직접 설치
# https://www.python.org/downloads/
```

### 문제 2: 가상 환경 활성화 실패

```
bash: venv/bin/activate: No such file or directory
```

**해결책**:
```bash
# 가상 환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### 문제 3: 의존성 설치 실패 (Apple Silicon)

```
error: unable to execute 'gcc': No such file or directory
```

**해결책**:
```bash
# Xcode Command Line Tools 설치
xcode-select --install

# 또는 재설치
sudo rm -rf /Library/Developer/CommandLineTools
xcode-select --install

# 그 후 의존성 재설치
pip install -r requirements.txt
```

### 문제 4: PySide6 import 오류

```
ModuleNotFoundError: No module named 'PySide6'
```

**해결책**:
```bash
# PySide6 재설치
pip uninstall PySide6 -y
pip install PySide6>=6.11
```

### 문제 5: yfinance 데이터 다운로드 오류

```
No data found for ticker [SYMBOL]
```

**원인**: Yahoo Finance API 형식 변경 (2025년 2월)

**해결책**:
```bash
# yfinance 업그레이드
pip install --upgrade yfinance

# 캐시 초기화
rm -rf ~/.cache/yfinance  # macOS 캐시 디렉터리
```

### 문제 6: matplotlib GUI 백엔드 오류

```
UserWarning: Matplotlib is currently using agg, which is a non-GUI backend
```

**해결책**:
```bash
# PyQt5 백엔드 강제 설정
export MPLBACKEND=Qt5Agg

# 또는 코드에서 설정
# (이미 src/main.py에서 처리됨)
```

### 문제 7: M1/M2 호환성 문제

```
ImportError: ... not compatible with this platform
```

**해결책**:
```bash
# Python 재설치 (arm64 버전 확인)
python3 -c "import platform; print(platform.machine())"
# arm64 출력되어야 함 (Apple Silicon)

# 가상 환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📝 자동 빌드 셸 스크립트

`build.sh` 파일 생성:

```bash
#!/bin/bash
set -e

echo ""
echo "================================"
echo "QuantInvest_Tool - macOS Build"
echo "================================"
echo ""

# 1. 가상 환경 활성화
echo "[1/5] 가상 환경 활성화 중..."
source venv/bin/activate || {
    echo "오류: 가상 환경을 활성화할 수 없습니다."
    exit 1
}

# 2. 의존성 설치
echo "[2/5] 의존성 설치 중..."
pip install -r requirements.txt pyinstaller>=6.16 -q || {
    echo "오류: 의존성 설치 실패"
    exit 1
}

# 3. 테스트 실행
echo "[3/5] 테스트 실행 중..."
pytest tests/ -q 2>/dev/null || echo "경고: 일부 테스트 실패 (계속 진행)"

# 4. 빌드 실행
echo "[4/5] PyInstaller 빌드 중..."
pyinstaller --clean --onefile --windowed \
    --name "QuantInvest_Tool" \
    --osx-bundle-identifier="com.quantinvest.tool" \
    src/main.py || {
    echo "오류: 빌드 실패"
    exit 1
}

# 5. 배포 준비
echo "[5/5] 배포 파일 준비 중..."
mkdir -p QuantInvest_Tool_v1.0.0
cp dist/QuantInvest\ Tool QuantInvest_Tool_v1.0.0/
cp README.md QuantInvest_Tool_v1.0.0/
cp ARCHITECTURE.md QuantInvest_Tool_v1.0.0/

echo ""
echo "================================"
echo "빌드 완료!"
echo "================================"
echo ""
echo "실행 파일: dist/QuantInvest_Tool"
echo "배포 패키지: QuantInvest_Tool_v1.0.0/"
echo ""
```

권한 추가 및 실행:
```bash
chmod +x build.sh
./build.sh
```

---

## 🎯 최종 체크리스트

빌드 전 확인:

```bash
# 1. 가상 환경 활성화
source venv/bin/activate

# 2. 최신 의존성 설치
pip install -r requirements.txt -U

# 3. 테스트 통과
pytest tests/ -q

# 4. 애플리케이션 수동 실행
python src/main.py

# 5. 빌드 도구 설치
pip install pyinstaller>=6.16

# 6. 캐시 정리
rm -rf build dist __pycache__

# 7. 최종 빌드
pyinstaller --clean --onefile --windowed src/main.py

# 8. 실행 파일 테스트
./dist/QuantInvest\ Tool
```

---

## 📊 빌드 결과 예상

| 항목 | 사항 |
|-----|------|
| 실행 파일 크기 | 150-200 MB |
| 실행 시간 | 2-3초 (첫 로드) |
| 요구 OS | macOS 11 이상 |
| 프로세서 | Intel / Apple Silicon 자동 감지 |
| 배포 | USB, 클라우드 스토리지, GitHub Release |

---

## 📞 지원

- **문서**: [README.md](README.md), [CLAUDE.md](CLAUDE.md), [ARCHITECTURE.md](ARCHITECTURE.md)
- **이슈**: https://github.com/smileplaza/QuantInvest_USA/issues
- **이메일**: sahong@kakao.com

---

**최종 업데이트**: 2026년 7월 24일 | **작성**: macOS 환경

✓ 설치 및 빌드 완료!
