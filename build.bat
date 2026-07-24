@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ================================
echo QuantInvest_Tool - Windows Build
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
pip install -r requirements.txt -q
pip install "pyinstaller>=6.16,<7" -q
if errorlevel 1 (
    echo 오류: 의존성 설치 실패
    pause
    exit /b 1
)

:: 3. 테스트 실행
echo [3/5] 테스트 실행 중...
set QT_QPA_PLATFORM=offscreen
python -m pytest tests/ -q
if errorlevel 1 (
    echo 경고: 일부 테스트 실패 ^(계속 진행^)
)

:: 4. 빌드 실행
echo [4/5] PyInstaller 빌드 중...
pyinstaller --clean --noconfirm QuantInvest.spec
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
copy "INSTALL_GUIDE_WINDOWS.md" "QuantInvest_Tool_v1.0.0\" >nul

echo.
echo ================================
echo 빌드 완료!
echo ================================
echo.
echo 실행 파일: dist\QuantInvest_Tool.exe
echo 배포 패키지: QuantInvest_Tool_v1.0.0\
echo.
pause
