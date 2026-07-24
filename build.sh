#!/bin/bash
set -e

echo ""
echo "================================"
echo "QuantInvest_Tool - Build (macOS/Linux)"
echo "================================"
echo ""

# 1. 가상 환경 활성화
echo "[1/5] 가상 환경 활성화 중..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 2. 의존성 설치
echo "[2/5] 의존성 설치 중..."
pip install -r requirements.txt -q
pip install "pyinstaller>=6.16,<7" -q

# 3. 테스트 실행
echo "[3/5] 테스트 실행 중..."
export QT_QPA_PLATFORM=offscreen
python -m pytest tests/ -q || echo "경고: 일부 테스트 실패 (계속 진행)"

# 4. 빌드 실행
echo "[4/5] PyInstaller 빌드 중..."
pyinstaller --clean --noconfirm QuantInvest.spec

# 5. 배포 준비
echo "[5/5] 배포 파일 준비 중..."
mkdir -p QuantInvest_Tool_v1.0.0
cp "dist/QuantInvest_Tool" QuantInvest_Tool_v1.0.0/ 2>/dev/null || true
cp README.md QuantInvest_Tool_v1.0.0/

echo ""
echo "================================"
echo "빌드 완료!"
echo "================================"
echo ""
echo "실행 파일: dist/QuantInvest_Tool"
echo "배포 패키지: QuantInvest_Tool_v1.0.0/"
echo ""
