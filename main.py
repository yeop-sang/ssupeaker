import os
import shutil
import pickle
import uuid
import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request, Query
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import uvicorn

from src.pipeline import MusicRecommendationPipeline
from src.speech_to_text import SpeechToText


# --- 전역 설정 ---
TEMP_UPLOAD_DIR = "temp_uploads"
EMBEDDING_DB_PATH = os.getenv("EMBEDDING_DB_PATH", "db/embeddings.pkl")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "bgm-selector-bucket")
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)


# --- FastAPI 앱 초기화 ---
app = FastAPI(
    title="콘텐츠 기반 음악 추천 API",
    description="오디오 내용(음성)을 이해하고, 분위기와 의미에 맞는 음악을 추천합니다.",
    version="2.0.0",
)


# --- 서버 시작 이벤트 ---
@app.on_event("startup")
def startup_event():
    """
    서버 시작 시, 미리 빌드된 음악 임베딩 DB를 로드하고 추천 파이프라인을 초기화합니다.
    - `db/embeddings.pkl` 파일이 반드시 존재해야 합니다.
    - 파일이 없으면 서버는 시작되지 않습니다.
    """
    print("--- 서버 시작 절차를 개시합니다 ---")
    
    db_path = Path(EMBEDDING_DB_PATH)
    
    if not db_path.is_file():
        print(f"치명적 오류: 임베딩 데이터베이스 파일을 찾을 수 없습니다. (경로: {EMBEDDING_DB_PATH})")
        print("-> 먼저 `scripts/build_embedding_db.py` 스크립트를 실행하여 DB를 생성해야 합니다.")
        # DB가 없으면 서버를 중지시킴
        raise RuntimeError("Embedding database not found. Cannot start server.")
        
    print(f"임베딩 데이터베이스를 로드합니다: {EMBEDDING_DB_PATH}")
    try:
        with open(db_path, "rb") as f:
            embedding_db = pickle.load(f)
        
        app.state.embedding_db = embedding_db
        app.state.pipeline = MusicRecommendationPipeline()
        print("✓ 음악 추천 파이프라인이 성공적으로 초기화되었습니다.")

    except Exception as e:
        print(f"치명적 오류: 임베딩 DB 로딩 또는 파이프라인 초기화 중 예외가 발생했습니다: {e}")
        raise RuntimeError("Failed to load DB or initialize pipeline.")
        
    print("--- 서버가 성공적으로 시작되었습니다 ---")


# --- Pydantic 모델 ---
class RecommendationResponse(BaseModel):
    file_name: str
    file_path: str
    score: float

# --- API 엔드포인트 ---
@app.get("/", summary="Health Check")
def health_check():
    """API 서버가 정상적으로 실행 중인지 확인합니다."""
    return {"status": "ok", "message": "API is running."}


@app.get("/generate-presigned-url/", summary="S3 파일용 임시 다운로드 URL 생성")
def generate_presigned_url(key: str = Query(..., description="S3 버킷 내의 파일 경로 (예: music_library/song1.mp3)")):
    """
    S3에 저장된 음악 파일에 접근할 수 있는 임시 URL(Pre-signed URL)을 생성합니다.
    이 URL은 1시간 동안 유효합니다.
    """
    s3_client = boto3.client('s3', region_name=os.getenv("AWS_REGION", "ap-northeast-2"))
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': key},
            ExpiresIn=3600  # URL 유효 시간 (초)
        )
        return {"url": url}
    except ClientError as e:
        print(f"S3 Pre-signed URL 생성 오류: {e}")
        # 파일이 존재하지 않거나 접근 권한이 없을 때
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없거나 접근 권한이 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {e}")


@app.post("/recommend/", response_model=List[RecommendationResponse], summary="음악 추천 받기")
async def recommend_music(file: UploadFile = File(..., description="음성 또는 음악이 담긴 오디오 파일")):
    """
    사용자가 업로드한 오디오 파일의 내용을 분석하여 가장 유사한 분위기의 음악을 추천합니다.
    """
    if not hasattr(app.state, 'pipeline') or app.state.pipeline is None:
        raise HTTPException(
            status_code=503, 
            detail="서버가 준비되지 않았습니다. 추천 파이프라인이 초기화되지 않았습니다."
        )

    # 1. 임시 파일 저장
    temp_file_path = Path(TEMP_UPLOAD_DIR) / f"{uuid.uuid4()}_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. 추천 파이프라인 실행
        print(f"오디오 파일 '{file.filename}'에 대한 추천을 시작합니다.")
        recommendations = app.state.pipeline.run(
            audio_path=str(temp_file_path),
            embedding_db=app.state.embedding_db,
        )
        print(f"추천 생성 완료: {len(recommendations)}개")

        return recommendations

    except Exception as e:
        print(f"오류: 추천 처리 중 예외 발생 - {e}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {e}")
    finally:
        # 3. 임시 파일 정리
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


if __name__ == "__main__":
    print("API 서버를 직접 실행합니다 (개발용).")
    print("배포 환경에서는 Gunicorn/Uvicorn 워커를 사용하세요.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
