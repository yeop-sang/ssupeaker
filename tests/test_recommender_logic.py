# -*- coding: utf-8 -*-
"""
AudioRecommender의 추천 로직 안정성 검증을 위한 유닛 테스트.

이 테스트 스크립트는 recommend_from_db 메서드가 다양한 조건,
특히 요청된 추천 개수(top_k)가 DB에 있는 아이템 수보다 많을 때도
안정적으로 동작하는지 검증하는 데 중점을 둡니다.
"""

import pytest
import torch
from src.recommender import AudioRecommender

@pytest.fixture
def recommender(mocker):
    """
    [Fixture] AI 모델 로딩 없이 AudioRecommender의 가짜 인스턴스를 생성하고,
    get_text_embedding 메서드를 모킹(mocking)합니다.
    """
    # __init__ 호출 없이 객체만 생성하여 무거운 모델 로딩을 건너뜁니다.
    recommender_instance = AudioRecommender.__new__(AudioRecommender)
    recommender_instance.device = "cpu"

    # 어떤 텍스트가 입력되든 항상 일관된 가짜 텍스트 임베딩을 반환하도록 모킹합니다.
    # 테스트의 초점은 추천 로직 자체이므로, 임베딩 생성 과정은 중요하지 않습니다.
    mocker.patch.object(
        recommender_instance, 
        "get_text_embedding", 
        return_value=torch.randn(1, 768) # 실제 CLAP 오디오 임베딩과 차원 맞춤
    )
    return recommender_instance

@pytest.fixture
def normal_embedding_db():
    """
    [Fixture] 정상 케이스 테스트를 위한 임베딩 데이터베이스 (10개 항목).
    top_k 요청(5)보다 데이터가 충분한 상황을 시뮬레이션합니다.
    """
    return [(f"path/song_{i}.mp3", torch.randn(1, 768)) for i in range(10)]

@pytest.fixture
def edge_case_embedding_db():
    """
    [Fixture] 엣지 케이스 테스트를 위한 임베딩 데이터베이스 (2개 항목).
    top_k 요청(5)보다 데이터가 부족한 상황을 시뮬레이션합니다.
    이것이 'list index out of range' 버그를 잡는 핵심 테스트입니다.
    """
    return [(f"path/edge_song_{i}.mp3", torch.randn(1, 768)) for i in range(2)]

def test_recommend_with_sufficient_data(recommender, normal_embedding_db):
    """
    [정상 케이스] DB에 노래가 충분할 때, 요청한 top_k 개수만큼 정확히 반환하는지 검증합니다.
    """
    # 준비
    target_text = "test"
    top_k = 5

    # 실행
    recommendations = recommender.recommend_from_db(
        target_text, normal_embedding_db, top_k=top_k
    )

    # 검증
    assert len(recommendations) == top_k, \
        f"DB에 노래가 10개 있을 때 top_k=5를 요청하면, 정확히 5개의 결과를 반환해야 합니다."

def test_recommend_with_insufficient_data(recommender, edge_case_embedding_db):
    """
    [엣지 케이스] DB에 노래가 부족할 때, 요청한 top_k보다 적은 수(DB의 전체 개수)를
    안전하게 반환하는지 검증합니다.
    """
    # 준비
    target_text = "test"
    top_k = 5
    num_songs_in_db = len(edge_case_embedding_db)

    # 실행
    # DB에는 2개의 노래만 있지만, 5개를 요청하는 상황입니다.
    recommendations = recommender.recommend_from_db(
        target_text, edge_case_embedding_db, top_k=top_k
    )

    # 검증
    # 오류 없이, DB에 있는 노래의 총개수인 2개만 반환되어야 합니다.
    assert len(recommendations) == num_songs_in_db, \
        f"DB에 노래가 2개 있을 때 top_k=5를 요청하면, 오류 없이 2개의 결과만 반환해야 합니다."

def test_recommend_with_empty_db(recommender):
    """
    [예외 케이스] 임베딩 DB가 비어있을 때, recommend_from_db 함수가
    적절한 예외(ValueError)를 발생시키는지 검증합니다.
    """
    with pytest.raises(ValueError, match="The provided embedding database is empty."):
        recommender.recommend_from_db("any text", [], top_k=5) 