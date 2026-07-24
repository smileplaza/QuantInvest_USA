# QuantInvest Tool — Windows 설치 및 컴파일 가이드

![Windows](https://img.shields.io/badge/Platform-Windows%2010%2B-0078d4?logo=windows)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776ab?logo=python)
![Status](https://img.shields.io/badge/Status-Production-28a745)

Windows에서 QuantInvest Tool을 설치하고 .exe 실행 파일로 빌드하는 완전한 가이드입니다.

## 📋 목차

- [시스템 요구사항](#시스템-요구사항)
- [사전 설치](#사전-설치)
- [단계별 설치](#단계별-설치)
- [애플리케이션 실행](#애플리케이션-실행)
- [PyInstaller로 .exe 빌드](#pyinstaller로-exe-빌드)
- [문제 해결](#문제-해결)

---

## 🖥️ 시스템 요구사항

### 최소 사양
- **OS**: Windows 10 이상
- **Python**: 3.12 ~ 3.14
- **RAM**: 4GB 이상
- **디스크**: 2GB (가상 환경 + 의존성)
- **인터넷**: 초기 설치 시 필수

### 확인 방법

```powershell
# Windows 버전 확인
[System.Environment]::OSVersion.VersionString

# 설치된 Python 확인 (있으면 버전 출력)
python --version
```

---

## 📦 사전 설치

### 1. Python 3.12+ 설치

**방법 1: python.org에서 직접 설치** (권장)

1. https://www.python.org/downloads/ 방문
2. "Download Python 3.12" (또는 최신 버전) 클릭
3. 설치 프로그램 실행
4. **중요**: "Add Python to PATH" 체크 ✓
5. "Install Now" 클릭

**방법 2: Microsoft Store**
```powershell
# Microsoft Store에서 검색 후 설치
# 또는 Windows Terminal에서
winget install Python.Python.3.12
```

**설치 확인**
```powershell
python --version
# Python 3.12.x 출력되어야 함

python -m pip --version
# pip 버전도 함께 확인
```

### 2. Git 설치 (저장소 클론용)

https://git-scm.com/ 에서 최신 버전 설치

또는 Windows Terminal:
```powershell
winget install Git.Git
```

**설치 확인**
```powershell
git --version
```

### 3. Visual Studio Build Tools (선택)

일부 Python 패키지(scipy, numpy)를 빌드할 때 필요할 수 있습니다.

```powershell
# C++ 빌드 도구 설치 (선택)
winget install Microsoft.VisualStudio.BuildTools
```

---

## 🚀 단계별 설치

### Step 1: 저장소 클론

```powershell
# 작업 디렉터리 이동 (예: C:\Projects)
cd C:\Projects

# 저장소 클론
git clone https://github.com/smileplaza/QuantInvest_USA.git
cd QuantInvest_USA
```

### Step 2: 가상 환경 생성 및 활성화

```powershell
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
.\venv\Scripts\activate

# 성공 확인 (프롬프트에 (venv) 표시)
# (venv) C:\Projects\QuantInvest_USA>
```

### Step 3: 패키지 업그레이드

```powershell
# pip 최신 버전으로 업데이트
python -m pip install --upgrade pip setuptools wheel
```

### Step 4: 의존성 설치

```powershell
# 런타임 의존성 설치
pip install -r requirements.txt

# 설치 확인
pip list | findstr /I "PySide6 pandas numpy yfinance"
```

### Step 5: 애플리케이션 실행 테스트

```powershell
# 애플리케이션 실행
python src/main.py
```

✓ GUI 창이 열리면 설치 성공!

---

## 🎮 애플리케이션 실행

### 일반 실행

```powershell
# 가상 환경 활성화 (필수)
.\venv\Scripts\activate

# 애플리케이션 실행
python src/main.py
```

### 단축키 생성 (선택)

바탕화면에 바로가기 생성:

```powershell
# PowerShell을 관리자 권한으로 실행한 후
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\QuantInvest Tool.lnk")
$Shortcut.TargetPath = "C:\Projects\QuantInvest_USA\venv\Scripts\pythonw.exe"
$Shortcut.Arguments = "C:\Projects\QuantInvest_USA\src\main.py"
$Shortcut.WorkingDirectory = "C:\Projects\QuantInvest_USA"
$Shortcut.Save()
```

---

## 🔨 PyInstaller로 .exe 빌드

### Step 1: 빌드 도구 설치

```powershell
# 가상 환경 활성화 필수
.\venv\Scripts\activate

# PyInstaller 설치
pip install pyinstaller>=6.16,<7
```

### Step 2: 자동 빌드 (간단함)

```powershell
# 한 줄 빌드 명령
pyinstaller --clean --onefile --windowed --name "QuantInvest_Tool" src/main.py

# 빌드 진행 상황 모니터링
# 2-3분 소요 (첫 빌드는 더 길 수 있음)
```

### Step 3: 빌드 결과 확인

```powershell
# 생성된 .exe 파일 확인
ls dist\

# 예상 출력:
# dist\
# └── QuantInvest_Tool.exe (150-200 MB)
```

### Step 4: .exe 테스트

```powershell
# .exe 실행 (GUI 창 열림)
.\dist\"QuantInvest_Tool.exe"
```

### Step 5: 배포용 준비

```powershell
# .exe 파일을 별도 폴더로 복사
New-Item -ItemType Directory -Force -Path "QuantInvest_Tool_v1.0.0" | Out-Null
Copy-Item "dist\QuantInvest_Tool.exe" "QuantInvest_Tool_v1.0.0\"
Copy-Item "README.md" "QuantInvest_Tool_v1.0.0\"
Copy-Item "ARCHITECTURE.md" "QuantInvest_Tool_v1.0.0\"

# ZIP으로 압축
Compress-Archive -Path "QuantInvest_Tool_v1.0.0" -DestinationPath "QuantInvest_Tool_v1.0.0.zip"
```

---

## 🔧 고급 빌드 옵션

### 아이콘 포함

```powershell
# icon.ico 파일이 있으면:
pyinstaller --clean --onefile --windowed `
  --name "QuantInvest Tool" `
  --icon=assets/icon.ico `
  src/main.py
```

### 버전 정보 포함

먼저 `version_info.txt` 생성:

```text
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(mask=0x3f, mask_set=0x3f, 
    productversion=(1,0,0,0), fileversion=(1,0,0,0),
    mask_set=0x3f),
  kids=[...],
  comments="정량 투자 전략 분석 도구",
  companyname="QuantInvest",
  fileversion="1.0.0",
  internalname="QuantInvest Tool",
  legallicense="MIT License",
  legaltrademarks="QuantInvest",
  originalname="QuantInvest_Tool.exe",
  productname="QuantInvest Tool",
  productversion="1.0.0"
)
```

그 후:
```powershell
pyinstaller --clean --onefile --windowed `
  --name "QuantInvest Tool" `
  --version-file=version_info.txt `
  src/main.py
```

### 최소화된 빌드

```powershell
# 디버그 정보 제거 (더 작은 파일)
pyinstaller --clean --onefile --windowed `
  --name "QuantInvest Tool" `
  --strip `
  src/main.py
```

---

## 📝 자동 빌드 배치 스크립트

`build.bat` 파일 생성:

```batch
@echo off
setlocal enabledelayedexpansion

echo.
echo ================================
echo QuantInvest Tool - Windows Build
echo ================================
echo.

:: 1. 가상 환경 활성화
echo [1/5] 가상 환경 활성화 중...
call .\venv\Scripts\activate.bat
if errorlevel 1 (
    echo 오류: 가상 환경을 활성화할 수 없습니다.
    pause
    exit /b 1
)

:: 2. 의존성 설치
echo [2/5] 의존성 설치 중...
pip install -r requirements.txt pyinstaller>=6.16 -q
if errorlevel 1 (
    echo 오류: 의존성 설치 실패
    pause
    exit /b 1
)

:: 3. 테스트 실행
echo [3/5] 테스트 실행 중...
pytest tests/ -q 2>nul
if errorlevel 1 (
    echo 경고: 일부 테스트 실패 (계속 진행)
)

:: 4. 빌드 실행
echo [4/5] PyInstaller 빌드 중...
pyinstaller --clean --onefile --windowed ^
    --name "QuantInvest Tool" ^
    src/main.py
if errorlevel 1 (
    echo 오류: 빌드 실패
    pause
    exit /b 1
)

:: 5. 배포 준비
echo [5/5] 배포 파일 준비 중...
if not exist "QuantInvest_Tool_v1.0.0" mkdir "QuantInvest_Tool_v1.0.0"
copy "dist\QuantInvest_Tool.exe" "QuantInvest_Tool_v1.0.0\" >nul
copy "README.md" "QuantInvest_Tool_v1.0.0\" >nul
copy "ARCHITECTURE.md" "QuantInvest_Tool_v1.0.0\" >nul

echo.
echo ================================
echo 빌드 완료!
echo ================================
echo.
echo 실행 파일: dist\QuantInvest_Tool.exe
echo 배포 패키지: QuantInvest_Tool_v1.0.0\
echo.
pause
```

실행:
```powershell
.\build.bat
```

---

## 🧪 테스트

### 단위 테스트 실행

```powershell
# 가상 환경 활성화 필수
.\venv\Scripts\activate

# 테스트 실행
pytest tests/ -v

# 커버리지 리포트
pytest tests/ --cov=src --cov-report=html
# 브라우저에서 htmlcov\index.html 확인
```

### 애플리케이션 스모크 테스트

```powershell
# 빠른 검증 (합성 데이터)
python -c "
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
print(f'✓ 백테스트 성공: CAGR {result[\"metrics\"][\"cagr\"]:.2%}')
"
```

---

## ⚠️ 문제 해결

### 문제 1: Python이 설치되지 않았음

```
'python' is not recognized as an internal or external command
```

**해결책**:
```powershell
# 1. Python 설치 확인
python --version

# 2. Python.org에서 설치 (위 참조)

# 3. 또는 PowerShell 재시작
# (PATH 업데이트를 위해)
```

### 문제 2: 가상 환경 활성화 실패

```
cannot be loaded because running scripts is disabled on this system
```

**해결책**:
```powershell
# PowerShell 정책 임시 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 그 후 다시 활성화
.\venv\Scripts\activate
```

### 문제 3: 의존성 설치 실패

```
error: Microsoft Visual C++ 14.0 is required
```

**해결책**:
```powershell
# Visual Studio Build Tools 설치
winget install Microsoft.VisualStudio.BuildTools

# 그 후 재시도
pip install -r requirements.txt
```

### 문제 4: PyInstaller 빌드 실패

```
ModuleNotFoundError: No module named 'PySide6'
```

**해결책**:
```powershell
# 명시적 hidden import 추가
pyinstaller --clean --onefile --windowed `
    --hidden-import=PySide6.QtCore `
    --hidden-import=PySide6.QtWidgets `
    --hidden-import=PySide6.QtGui `
    src/main.py

# 또는 캐시 제거 후 재빌드
rm -r build, dist, __pycache__
pyinstaller --clean --onefile --windowed src/main.py
```

### 문제 5: .exe 시작 안 됨

**진단**:
```powershell
# 명령줄에서 실행하여 오류 메시지 확인
.\dist\"QuantInvest_Tool.exe"

# 또는 이벤트 뷰어 확인
eventvwr.msc
```

**해결책**:
```powershell
# 의존성 재확인
pip install -r requirements.txt --force-reinstall

# 정리 후 재빌드
rm -r build, dist
pyinstaller --clean --onefile --windowed --name "QuantInvest_Tool" src/main.py
```

### 문제 6: yfinance 데이터 다운로드 오류

```
No data found for ticker [SYMBOL]
```

**원인**: Yahoo Finance API 형식 변경 (2025년 2월)

**해결책**: 이미 수정됨
- yfinance >= 1.5.2 설치
- `src/data/downloader.py`에서 다음 옵션 확인:
  ```python
  yf.download(..., multi_level_index=False, auto_adjust=False)
  ```

---

## 📊 최종 체크리스트

빌드 전 확인:

```powershell
# 1. 가상 환경 활성화
.\venv\Scripts\activate

# 2. 최신 의존성 설치
pip install -r requirements.txt -U

# 3. 테스트 통과
pytest tests/ -q

# 4. 애플리케이션 수동 실행
python src/main.py

# 5. 빌드 도구 설치
pip install pyinstaller>=6.16

# 6. 캐시 정리
rm -r build, dist -Force

# 7. 최종 빌드
pyinstaller --clean --onefile --windowed src/main.py

# 8. .exe 테스트
.\dist\"QuantInvest_Tool.exe"
```

---

## 📞 지원

- **문서**: [README.md](README.md), [CLAUDE.md](CLAUDE.md), [ARCHITECTURE.md](ARCHITECTURE.md)
- **이슈**: https://github.com/smileplaza/QuantInvest_USA/issues
- **이메일**: sahong@kakao.com

---

**최종 업데이트**: 2026년 7월 24일 | **작성**: Windows 환경

✓ 설치 및 빌드 완료!
