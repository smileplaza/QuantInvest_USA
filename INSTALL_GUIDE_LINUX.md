# QuantInvest_Tool — Linux 설치 및 컴파일 가이드

![Linux](https://img.shields.io/badge/Platform-Linux-FCC624?logo=linux)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776ab?logo=python)
![Status](https://img.shields.io/badge/Status-Production-28a745)

Linux(Ubuntu, Debian, CentOS, Fedora 등)에서 QuantInvest_Tool을 설치하고 실행하는 완전한 가이드입니다.

## 📋 목차

- [지원되는 배포판](#지원되는-배포판)
- [시스템 요구사항](#시스템-요구사항)
- [사전 설치](#사전-설치)
- [단계별 설치](#단계별-설치)
- [애플리케이션 실행](#애플리케이션-실행)
- [Linux 데스크톱 통합 (선택)](#linux-데스크톱-통합-선택)
- [문제 해결](#문제-해결)

---

## 🐧 지원되는 배포판

| 배포판 | 버전 | 상태 |
|-------|------|------|
| Ubuntu | 22.04 LTS, 24.04 LTS | ✓ 완벽 지원 |
| Debian | 12 (Bookworm) | ✓ 완벽 지원 |
| Fedora | 40, 41, 42 | ✓ 완벽 지원 |
| CentOS | 8+ / RHEL 9+ | ✓ 지원 |
| Linux Mint | 21, 22 | ✓ 지원 |
| Elementary OS | 7.0 | ✓ 지원 |

---

## 🖥️ 시스템 요구사항

### 최소 사양
- **OS**: Linux (커널 5.0+)
- **Python**: 3.12 ~ 3.14
- **RAM**: 4GB 이상
- **디스크**: 2GB (가상 환경 + 의존성)
- **DE/WM**: X11 또는 Wayland (PySide6 호환)
- **인터넷**: 초기 설치 시 필수

### 확인 방법

```bash
# Linux 배포판 확인
cat /etc/os-release

# 커널 버전 확인
uname -r

# 설치된 Python 확인
python3 --version
```

---

## 📦 사전 설치

### 1. 시스템 패키지 업데이트

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt upgrade -y
```

**Fedora/CentOS/RHEL:**
```bash
sudo dnf update -y
# 또는
sudo yum update -y
```

### 2. Python 3.12+ 설치

**Ubuntu 24.04 / Debian 12:**
```bash
# Python 3.12는 기본 제공
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip
```

**Ubuntu 22.04 / Debian 11 (더 오래된 버전):**
```bash
# Python 3.12 추가 저장소에서 설치
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip
```

**Fedora 40+:**
```bash
sudo dnf install -y python3.12 python3-pip gcc-c++ python3-devel
```

**CentOS/RHEL 9:**
```bash
sudo dnf install -y python3.12 python3-pip gcc-c++ python3-devel
```

**설치 확인**
```bash
python3.12 --version
python3.12 -m pip --version
```

### 3. 필수 개발 도구 설치

**Ubuntu/Debian:**
```bash
sudo apt install -y \
  build-essential \
  libssl-dev \
  libffi-dev \
  python3-dev \
  git \
  libgl1-mesa-glx \
  libxkbcommon-x11-0
```

**Fedora:**
```bash
sudo dnf install -y \
  gcc \
  gcc-c++ \
  make \
  openssl-devel \
  python3-devel \
  git \
  mesa-libGL \
  libxkbcommon-x11
```

### 4. X11 라이브러리 (GUI 렌더링용)

**Ubuntu/Debian (Wayland 사용자):**
```bash
# Wayland에서도 X11 지원 활성화
sudo apt install -y xwayland
```

---

## 🚀 단계별 설치

### Step 1: 저장소 클론

```bash
# 작업 디렉터리 이동 (예: ~/projects)
mkdir -p ~/projects
cd ~/projects

# 저장소 클론
git clone https://github.com/smileplaza/QuantInvest_USA.git
cd QuantInvest_USA
```

### Step 2: 가상 환경 생성 및 활성화

```bash
# 가상 환경 생성
python3.12 -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# 성공 확인 (프롬프트에 (venv) 표시)
# (venv) user@linux:~/projects/QuantInvest_USA$
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

> **참고**: 설치 시간은 5-15분 정도 소요될 수 있습니다.

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
# nohup으로 백그라운드 실행
nohup python src/main.py > /dev/null 2>&1 &

# 프로세스 종료
pkill -f "python src/main.py"
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

### systemd 서비스 등록 (고급)

`quantinvest.service` 파일 생성 (`/etc/systemd/system/`에):

```ini
[Unit]
Description=QuantInvest_Tool
After=network.target display-manager.service

[Service]
User=$USER
Type=simple
ExecStart=/home/$USER/projects/QuantInvest_USA/venv/bin/python /home/$USER/projects/QuantInvest_USA/src/main.py
Restart=on-failure
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/$USER/.Xauthority"

[Install]
WantedBy=multi-user.target graphical.target
```

등록:
```bash
sudo systemctl daemon-reload
sudo systemctl enable quantinvest
sudo systemctl start quantinvest
```

---

## 📦 Linux 데스크톱 통합 (선택)

### .desktop 파일 생성

`$HOME/.local/share/applications/quantinvest.desktop` 생성:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=QuantInvest_Tool
Comment=정량 투자 전략 분석 도구
Icon=python
Exec=/home/$USER/projects/QuantInvest_USA/run.sh
Path=/home/$USER/projects/QuantInvest_USA
Terminal=false
Categories=Finance;Office;
```

> **주의**: `$USER`를 실제 사용자 이름으로 변경하세요.

실제 경로로 편집:
```bash
# 템플릿 생성
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/quantinvest.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=QuantInvest_Tool
Comment=정량 투자 전략 분석 도구
Icon=python
Exec=$HOME/projects/QuantInvest_USA/run.sh
Path=$HOME/projects/QuantInvest_USA
Terminal=false
Categories=Finance;Office;
EOF

# 응용프로그램 메뉴에 나타남
```

### 아이콘 설정 (선택)

```bash
# 아이콘 파일 복사
mkdir -p ~/.local/share/icons/hicolor/256x256/apps
cp assets/icon.png ~/.local/share/icons/hicolor/256x256/apps/quantinvest.png

# 또는 .desktop 파일에서 Icon 경로 지정
Icon=$HOME/projects/QuantInvest_USA/assets/icon.png
```

---

## 🔧 PyInstaller로 실행 파일 생성

### Step 1: PyInstaller 설치

```bash
# 가상 환경 활성화 필수
source venv/bin/activate

# PyInstaller 설치
pip install pyinstaller>=6.16,<7
```

### Step 2: 빌드

```bash
# Linux용 실행 파일 생성
pyinstaller --clean --onefile --windowed \
  --name "QuantInvest_Tool" \
  src/main.py
```

### Step 3: 결과 확인

```bash
# 생성된 파일 확인
ls -lh dist/

# 예상 출력:
# QuantInvest_Tool (150-200 MB)
```

### Step 4: 실행 테스트

```bash
# 실행
./dist/QuantInvest\ Tool
```

### Step 5: AppImage 생성 (배포용)

```bash
# AppImage 도구 설치
pip install pyinstaller-with-appimage

# 또는 appimagetool 직접 설치
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool

# AppImage 생성
pyinstaller --onefile --windowed --name "QuantInvest_Tool" src/main.py
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
xdg-open htmlcov/index.html
```

### 애플리케이션 스모크 테스트

```bash
# 빠른 검증 (합성 데이터)
source venv/bin/activate
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

### 문제 1: Python 3.12 설치 불가

```
E: Unable to locate package python3.12
```

**해결책 (Ubuntu 22.04):**
```bash
# deadsnakes PPA 추가
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv
```

### 문제 2: PySide6 import 오류

```
ImportError: libGL.so.1: cannot open shared object file
```

**해결책:**
```bash
# Ubuntu/Debian
sudo apt install -y libgl1-mesa-glx libxkbcommon-x11-0 libdbus-1-3

# Fedora
sudo dnf install -y mesa-libGL libxkbcommon-x11 dbus-libs
```

### 문제 3: Wayland 세션에서 GUI 안 열림

```
Cannot connect to display
```

**해결책:**
```bash
# X11 세션으로 변경 (로그인 화면에서)
# 또는 Xwayland 설치
sudo apt install -y xwayland

# 또는 명시적으로 X11 강제
export QT_QPA_PLATFORM=xcb
python src/main.py
```

### 문제 4: 의존성 설치 실패

```
error: 'python.h' file not found
```

**해결책:**
```bash
# Ubuntu/Debian
sudo apt install -y python3.12-dev libpython3.12-dev

# Fedora
sudo dnf install -y python3-devel

# CentOS/RHEL
sudo yum install -y python3-devel
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
rm -rf ~/.cache/pip
```

### 문제 6: 권한 부족

```
PermissionError: [Errno 13] Permission denied
```

**해결책:**
```bash
# 프로젝트 소유권 확인
ls -la ~/projects/QuantInvest_USA/

# 필요시 권한 변경
chmod -R u+rwx ~/projects/QuantInvest_USA/
```

### 문제 7: 디스플레이 연결 문제 (원격 서버)

```
Could not connect to display
```

**해결책:**
```bash
# X11 포워딩 활성화
ssh -X user@server

# 또는 가상 디스플레이 생성
Xvfb :99 &
export DISPLAY=:99
python src/main.py
```

---

## 📝 자동 빌드 셸 스크립트

`build.sh` 파일 생성:

```bash
#!/bin/bash
set -e

echo ""
echo "================================"
echo "QuantInvest_Tool - Linux Build"
echo "================================"
echo ""

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 가상 환경 활성화
echo "[1/5] 가상 환경 활성화 중..."
if [ ! -d "venv" ]; then
    python3.12 -m venv venv || {
        echo -e "${RED}오류: 가상 환경을 생성할 수 없습니다.${NC}"
        exit 1
    }
fi

source venv/bin/activate || {
    echo -e "${RED}오류: 가상 환경을 활성화할 수 없습니다.${NC}"
    exit 1
}

# 2. 의존성 설치
echo "[2/5] 의존성 설치 중..."
pip install -r requirements.txt pyinstaller>=6.16 -q || {
    echo -e "${RED}오류: 의존성 설치 실패${NC}"
    exit 1
}

# 3. 테스트 실행
echo "[3/5] 테스트 실행 중..."
pytest tests/ -q 2>/dev/null || echo "경고: 일부 테스트 실패 (계속 진행)"

# 4. 빌드 실행
echo "[4/5] PyInstaller 빌드 중..."
pyinstaller --clean --onefile --windowed \
    --name "QuantInvest_Tool" \
    src/main.py || {
    echo -e "${RED}오류: 빌드 실패${NC}"
    exit 1
}

# 5. 배포 준비
echo "[5/5] 배포 파일 준비 중..."
mkdir -p QuantInvest_Tool_v1.0.0
cp "dist/QuantInvest_Tool" QuantInvest_Tool_v1.0.0/
cp README.md QuantInvest_Tool_v1.0.0/
cp ARCHITECTURE.md QuantInvest_Tool_v1.0.0/

echo ""
echo "================================"
echo -e "${GREEN}빌드 완료!${NC}"
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

# 2. Python 버전 확인
python --version

# 3. 최신 의존성 설치
pip install -r requirements.txt -U

# 4. 테스트 통과
pytest tests/ -q

# 5. 애플리케이션 수동 실행
python src/main.py

# 6. 빌드 도구 설치
pip install pyinstaller>=6.16

# 7. 캐시 정리
rm -rf build dist __pycache__

# 8. 최종 빌드
pyinstaller --clean --onefile --windowed src/main.py

# 9. 실행 파일 테스트
"./dist/QuantInvest_Tool"
```

---

## 📊 빌드 결과 예상

| 항목 | 사항 |
|-----|------|
| 실행 파일 크기 | 150-200 MB |
| 실행 시간 | 2-3초 (첫 로드) |
| 요구 OS | Linux (glibc 2.31+) |
| DE/WM | X11, Wayland (Xwayland 포함) |
| 배포 | AppImage, Flatpak, 소스 코드 |

---

## 🐳 Docker로 실행 (선택)

### Dockerfile 생성

```dockerfile
FROM ubuntu:24.04

WORKDIR /app

# 의존성 설치
RUN apt update && apt install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    git \
    libgl1-mesa-glx \
    libxkbcommon-x11-0

# 코드 복사
COPY . .

# 가상 환경 생성
RUN python3.12 -m venv venv
RUN . venv/bin/activate && pip install -r requirements.txt

# GUI 모드 지원 (X11 포워딩)
ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1

# 실행
CMD ["/bin/bash", "-c", ". venv/bin/activate && python src/main.py"]
```

빌드 및 실행:
```bash
# 이미지 빌드
docker build -t quantinvest:latest .

# X11 포워딩으로 실행
docker run -it \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $HOME/.Xauthority:/home/user/.Xauthority \
    quantinvest:latest
```

---

## 📞 지원

- **문서**: [README.md](README.md), [CLAUDE.md](CLAUDE.md), [ARCHITECTURE.md](ARCHITECTURE.md)
- **이슈**: https://github.com/smileplaza/QuantInvest_USA/issues
- **이메일**: sahong@gmarket.com

---

**최종 업데이트**: 2026년 7월 24일 | **작성**: Linux 환경

✓ 설치 및 빌드 완료!
