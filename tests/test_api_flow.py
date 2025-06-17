# -*- coding: utf-8 -*-
"""
API 통합 테스트 스크립트.

이 파일은 FastAPI 애플리케이션의 엔드포인트가 실제 요청에 대해 예상대로 동작하는지
검증합니다. 파일 업로드, 임베딩 DB 로딩, 추천 파이프라인 실행, 결과 반환 등
전체 시나리오를 포함하는 통합 테스트(Integration Test)입니다.
"""

import pytest
import pickle
import torch
import numpy as np
import scipy.io.wavfile
from fastapi.testclient import TestClient
from pathlib import Path

# 테스트 클라이언트가 FastAPI 앱을 인식하도록 `main`에서 `app` 객체를 가져옵니다.
from main import app

# 테스트 클라이언트 인스턴스를 생성합니다.
# 이 클라이언트를 통해 실제 네트워크 호출 없이 메모리상에서 API 요청을 보낼 수 있습니다.
client = TestClient(app)


@pytest.fixture(scope="module")
def test_audio_file(tmp_path_factory):
    """
    [Fixture] API 엔드포인트 테스트에 사용할 임시 WAV 오디오 파일을 생성합니다.

    - `scope="module"`: Fixture가 모듈 단위로 한 번만 실행되어 불필요한 반복 생성을 방지합니다.
    - `tmp_path_factory`: Pytest가 제공하는 임시 디렉토리/파일 생성 유틸리티입니다.
    
    반환값:
        Path: 생성된 임시 WAV 파일의 경로 객체.
    """
    # 모듈 범위의 임시 디렉토리를 생성합니다.
    audio_dir = tmp_path_factory.mktemp("test_audio")
    file_path = audio_dir / "silent_audio.wav"
    
    # 1초 길이의 무음(silent) 오디오 데이터를 생성합니다.
    # API 테스트에서는 오디오 내용보다 파일 형식과 전송 과정이 중요합니다.
    samplerate = 16000  # 16kHz 샘플링 속도
    duration_seconds = 1
    silent_data = np.zeros((samplerate * duration_seconds,), dtype=np.int16)
    
    # 생성된 데이터를 WAV 파일로 저장합니다.
    scipy.io.wavfile.write(file_path, samplerate, silent_data)
    
    return file_path


@pytest.fixture(scope="module")
def test_embedding_db(tmp_path_factory):
    """
    [Fixture] 서버 시작 시 로드할 임시 음악 임베딩 데이터베이스(.pkl)를 생성합니다.

    실제 DB 대신 가짜 DB를 사용함으로써 테스트의 독립성을 확보하고,
    DB 내용에 따라 예측 가능한 결과를 검증할 수 있습니다.
    
    반환값:
        Path: 생성된 임시 DB 파일의 경로 객체.
    """
    db_dir = tmp_path_factory.mktemp("test_db")
    db_path = db_dir / "test_embeddings.pkl"
    
    # 데이터베이스는 `(파일경로, 텐서)` 튜플의 리스트 형태여야 합니다.
    test_db_content = [
        ("test_music/song_1.wav", torch.randn(1, 768)),
        ("test_music/song_2.wav", torch.randn(1, 768)),
    ]
    
    # Pickle을 사용하여 직렬화된 DB 파일을 생성합니다.
    with open(db_path, "wb") as f:
        pickle.dump(test_db_content, f)
        
    return db_path


def test_recommend_endpoint_success(monkeypatch, test_audio_file, test_embedding_db):
    """
    [성공 케이스] `/recommend/` 엔드포인트의 정상적인 전체 흐름을 테스트합니다.
    
    - `monkeypatch`: 테스트 중에 환경 변수나 객체의 속성을 동적으로 변경합니다.
    - `test_audio_file`, `test_embedding_db`: 위에서 정의한 Fixture들입니다.
    """
    # 준비: main 모듈의 `EMBEDDING_DB_PATH`를 테스트용 DB 경로로 교체합니다.
    # 이를 통해 실제 프로덕션 DB 대신 격리된 테스트 DB를 사용하게 됩니다.
    monkeypatch.setattr("main.EMBEDDING_DB_PATH", str(test_embedding_db))

    # `stt.transcribe` 메서드를 모킹하여 항상 고정된 텍스트를 반환하도록 설정합니다.
    # 이렇게 하면 실제 음성 인식 모델의 성능과 무관하게 API 흐름을 테스트할 수 있습니다.
    monkeypatch.setattr(
        "src.pipeline.SpeechToText.transcribe",
        lambda self, audio_path: "a happy song"
    )

    # 실행 및 검증: `TestClient` 컨텍스트 내에서 API의 생명주기(startup/shutdown)를 관리합니다.
    with TestClient(app) as client:
        
        # 업로드할 오디오 파일을 바이너리 읽기 모드로 엽니다.
        with open(test_audio_file, "rb") as audio_file:
            # FastAPI `TestClient`가 요구하는 파일 업로드 형식에 맞춥니다.
            # `(파일명, 파일객체, 미디어타입)` 튜플 형식입니다.
            files_to_upload = {"file": (test_audio_file.name, audio_file, "audio/wav")}

            # `/recommend/` 엔드포인트에 POST 요청을 보냅니다.
            response = client.post("/recommend/", files=files_to_upload)

            # 응답 코드가 200 (성공)인지 확인합니다.
            assert response.status_code == 200, f"예상 상태 코드 200, 실제: {response.status_code}"
            
            # 응답 본문(JSON)을 파싱하고 구조를 검증합니다.
            response_data = response.json()
            assert isinstance(response_data, list), "응답 본문은 리스트(JSON 배열) 형식이어야 합니다."
            assert len(response_data) > 0, "최소 하나 이상의 추천 결과가 반환되어야 합니다."
            
            # 첫 번째 추천 결과의 필수 필드 존재 여부를 확인합니다.
            first_recommendation = response_data[0]
            assert "file_name" in first_recommendation
            assert "file_path" in first_recommendation
            assert "score" in first_recommendation, "각 추천 결과에는 'score' 필드가 포함되어야 합니다."


def test_server_startup_fails_if_db_not_found(monkeypatch):
    """
    [실패 케이스] 임베딩 DB 파일이 존재하지 않을 때 서버 시작이 정상적으로 실패하는지 검증합니다.
    
    `main.py`의 `startup_event`는 DB 파일이 없으면 `RuntimeError`를 발생시켜야 합니다.
    """
    # 준비: 존재하지 않는 DB 파일 경로로 `EMBEDDING_DB_PATH`를 덮어씁니다.
    non_existent_db_path = "/path/that/does/not/exist/db.pkl"
    monkeypatch.setattr("main.EMBEDDING_DB_PATH", non_existent_db_path)

    # 실행 및 검증: `pytest.raises`를 사용하여 `RuntimeError`가 발생하는 것을 확인합니다.
    # 이 컨텍스트 블록 안에서 `RuntimeError`가 발생하면 테스트는 성공으로 간주됩니다.
    with pytest.raises(RuntimeError) as excinfo:
        # `TestClient`를 초기화하는 과정에서 `startup` 이벤트가 호출됩니다.
        with TestClient(app):
            pass  # `startup` 이벤트 실행을 위해 컨텍스트만 열고 닫습니다.

    # 발생한 예외 메시지가 예상된 내용을 포함하는지 확인하여,
    # 의도된 오류로 인해 실패했는지 검증합니다.
    assert "Embedding database not found" in str(excinfo.value) 