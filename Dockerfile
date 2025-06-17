# 1. 베이스 이미지 설정: 가볍고 안정적인 python:3.9-slim-bullseye 사용
FROM python:3.9-slim-bullseye

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. Debian APT 저장소를 한국 미러(KAIST)로 변경하여 네트워크 속도 향상
RUN sed -i 's/deb.debian.org/ftp.kaist.ac.kr/g' /etc/apt/sources.list

# 4. 시스템 의존성 설치: MySQL 클라이언트, 빌드 도구, FFmpeg
# apt-get update로 패키지 목록을 최신화하고, 필요한 패키지를 설치합니다.
# --no-install-recommends 플래그로 불필요한 패키지 설치를 방지하고,
# 설치 후에는 apt 캐시를 정리하여 이미지 크기를 줄입니다.
RUN apt-get update && apt-get install -y default-mysql-client build-essential ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 5. Python 의존성 설치
# requirements.txt를 먼저 복사하여 레이어 캐싱을 활용합니다.
# 이렇게 하면 requirements.txt가 변경되지 않는 한, pip install을 다시 실행하지 않아 빌드 속도가 향상됩니다.
COPY requirements.txt .
RUN pip install -r requirements.txt

# 6. 프로젝트 소스 코드 복사
# 나머지 모든 소스 코드를 작업 디렉토리로 복사합니다.
COPY . .

# 7. entrypoint.sh에 실행 권한 부여
RUN chmod +x /app/entrypoint.sh

# 8. 컨테이너 실행 설정
# entrypoint.sh를 통해 컨테이너 시작 작업을 수행하고,
# CMD로 uvicorn 서버 실행 명령을 전달합니다.
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 