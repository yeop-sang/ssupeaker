#!/bin/bash

# --- 환경 변수 설정 ---
# 프로젝트의 .venv 가상 환경 경로를 지정합니다.
VENV_PATH="./.venv"
PYTHON_EXEC="$VENV_PATH/bin/python"

# 1. 가상 환경 확인
# .venv 디렉토리가 존재하는지 확인합니다.
if [ ! -d "$VENV_PATH" ]; then
    echo "오류: .venv 가상 환경을 찾을 수 없습니다."
    echo "먼저 'python -m venv .venv' 명령어로 가상 환경을 생성하고,"
    echo "'source .venv/bin/activate'로 활성화한 후,"
    echo "'pip install -r requirements.txt'로 의존성을 설치해주세요."
    exit 1
fi

# 실행할 Python 실행 파일이 실제로 존재하는지 확인합니다.
if [ ! -f "$PYTHON_EXEC" ]; then
    echo "오류: 가상 환경에서 Python 실행 파일($PYTHON_EXEC)을 찾을 수 없습니다."
    exit 1
fi

echo "pytest를 실행합니다..."
echo "======================"

# 2. pytest 실행 및 3. 유연한 인자 전달
# 가상 환경의 python으로 pytest 모듈을 실행합니다.
# 이 스크립트에 전달된 모든 인자($@)를 pytest 명령어에 그대로 전달합니다.
"$PYTHON_EXEC" -m pytest "$@"

echo "======================"
echo "pytest 실행이 완료되었습니다." 