#!/bin/bash

# 스크립트 실행 중 오류가 발생하면 즉시 중단합니다.
set -e

# --- 설정 ---
PYTHON_VERSION="3.9.18"
VENV_DIR="temp_music_env" # 가상 환경 폴더 이름
SCRIPT_PATH="src/music_downloader.py"

# --- 스크립트 시작 ---
echo "Python 스크립트 실행 및 환경 정리 프로세스를 시작합니다."

# pyenv 초기화
if ! command -v pyenv &> /dev/null; then
    echo "오류: pyenv가 설치되어 있지 않습니다."
    exit 1
fi
eval "$(pyenv init -)"

# 1. 특정 Python 버전 설치 (사용자 요청으로 주석 처리)
# echo "1/5: Python 버전($PYTHON_VERSION) 설치 확인 및 진행..."
# pyenv install --skip-existing $PYTHON_VERSION

# 2. 표준 venv를 사용하여 가상 환경 생성
echo "2/5: Python 내장 'venv'를 사용하여 가상 환경($VENV_DIR)을 생성합니다..."
# 기존 폴더가 있으면 삭제
if [ -d "$VENV_DIR" ]; then
    echo "기존 가상 환경 폴더($VENV_DIR)를 삭제합니다."
    rm -rf "$VENV_DIR"
fi
# pyenv로 특정 버전의 python을 지정하여 venv 생성
pyenv shell $PYTHON_VERSION
PYTHON_EXEC=$(pyenv which python3)
"$PYTHON_EXEC" -m venv "$VENV_DIR"
echo "가상 환경 생성이 완료되었습니다."

# 3. 스크립트에 필요한 라이브러리 설치
echo "3/5: 필요한 라이브러리를 가상 환경에 설치합니다..."
# 생성된 가상 환경의 pip를 직접 사용
./$VENV_DIR/bin/pip install requests beautifulsoup4 selenium webdriver-manager

# 4. Python 스크립트 실행
echo "4/5: Python 스크립트($SCRIPT_PATH)를 실행합니다..."
# 생성된 가상 환경의 python을 직접 사용
./$VENV_DIR/bin/python $SCRIPT_PATH

# 5. 생성된 가상 환경 폴더 제거
echo "5/5: 정리 작업을 시작합니다..."
echo "가상 환경 폴더($VENV_DIR)를 삭제합니다."
rm -rf "$VENV_DIR"

# 스크립트 파일은 사용자 요청으로 삭제하지 않음
# echo "스크립트 파일($SCRIPT_PATH)을 삭제합니다."
# rm -f $SCRIPT_PATH

echo "모든 작업이 완료되었습니다." 