#!/bin/bash

# 스크립트 실행 중 오류가 발생하면 즉시 중단합니다.
set -e

# --- 환경 변수 설정 ---
# Conda 가상 환경의 경로를 지정하여 안정성을 높입니다.
CONDA_ENV_PATH="/Users/sangyeop/miniconda3/envs/ssupeaker-env"
PYTHON_EXEC="$CONDA_ENV_PATH/bin/python"
UVICORN_EXEC="$CONDA_ENV_PATH/bin/uvicorn"

# Conda 환경이 존재하는지 확인합니다.
if [ ! -f "$PYTHON_EXEC" ]; then
    echo "오류: Conda 가상 환경 'ssupeaker-env'를 찾을 수 없습니다."
    echo "먼저 'conda activate ssupeaker-env' 명령어로 환경이 활성화되는지 확인해주세요."
    exit 1
fi

echo "SSUPEAKER 로컬 테스트 환경 설정을 시작합니다."
echo "============================================"
echo ""

# 1. 테스트용 디렉토리 생성
echo "1. 테스트용 디렉토리를 생성합니다..."
mkdir -p db
mkdir -p music_library
echo "  -> 'db'와 'music_library' 폴더가 준비되었습니다."
echo ""

# 2. 사용자 입력 대기
echo "2. 'music_library' 폴더에 테스트용 음악 파일을 넣어주세요."
read -p "   준비가 완료되면 Enter 키를 눌러주세요..."
echo ""

# 3. 임베딩 데이터베이스 생성
echo "3. 임베딩 데이터베이스를 생성합니다... (음악 파일 개수에 따라 시간이 걸릴 수 있습니다)"
"$PYTHON_EXEC" -c "from src.utils.build_embedding_db import build_embedding_database; build_embedding_database(music_dir_path='./music_library', output_db_path='./db/embeddings.pkl')"
echo "  -> 데이터베이스 생성이 완료되었습니다."
echo ""

# 4. FastAPI 서버 실행
echo "4. FastAPI 서버를 시작합니다..."
echo "   - 서버 주소: http://127.0.0.1:8000"
echo "   - API 문서: http://12.0.0.1:8000/docs"
echo "   - (서버를 종료하려면 Ctrl+C를 누르세요)"
echo ""
"$UVICORN_EXEC" main:app --reload

echo "============================================"
echo "로컬 테스트 환경이 종료되었습니다." 