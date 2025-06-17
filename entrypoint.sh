#!/bin/sh
set -e

# 환경 변수 확인 (선택 사항이지만 디버깅에 유용)
echo "S3_BUCKET_NAME: ${S3_BUCKET_NAME:-'bgm-selector-bucket'}"
echo "DB_S3_KEY: ${DB_S3_KEY:-'db/embeddings.pkl'}"
DB_LOCAL_PATH="/app/db/embeddings.pkl"

# 로컬 DB 디렉토리 생성
mkdir -p /app/db

# 1. S3에서 임베딩 데이터베이스 파일 다운로드
echo "S3에서 임베딩 데이터베이스를 다운로드합니다..."
aws s3 cp "s3://${S3_BUCKET_NAME:-'bgm-selector-bucket'}/${DB_S3_KEY:-'db/embeddings.pkl'}" "${DB_LOCAL_PATH}"

# 파일 다운로드 확인
if [ ! -f "${DB_LOCAL_PATH}" ]; then
    echo "치명적 오류: S3에서 DB 파일을 다운로드하지 못했습니다."
    exit 1
fi

echo "DB 다운로드 완료."

# 2. FastAPI 애플리케이션 실행
# exec "$@"는 CMD로 전달된 명령어를 실행합니다.
# 이렇게 하면 uvicorn이 PID 1이 되어 Docker의 시그널을 제대로 처리할 수 있습니다.
echo "FastAPI 서버를 시작합니다..."
exec "$@" 