import os
from src.recommender import AudioRecommender
from typing import List, Dict, Tuple
import torch


class MusicRecommendationPipeline:
    def __init__(self, whisper_model_size="base", device=None):
        """
        음악 추천 파이프라인의 모든 구성 요소를 초기화합니다.
        """
        self.device = device
        print("Initializing pipeline components...")
        self.recommender = AudioRecommender(whisper_model_size=whisper_model_size, device=self.device)
        print("Pipeline initialized.")

    def run(self, audio_path: str) -> List[str]:
        """
        전체 음악 추천 파이프라인을 실행합니다.

        Args:
            audio_path (str): 입력 오디오 파일의 경로.

        Returns:
            추천된 음악 파일 이름의 리스트.
        """
        if not os.path.exists(audio_path):
            print(f"오류: 입력 오디오 파일을 찾을 수 없습니다: {audio_path}")
            return []

        # 단계 1: 음성을 텍스트로 변환
        print("\n--- 단계 1: 음성 텍스트 변환 ---")
        print(f"음성 인식을 위해 다음 파일을 사용합니다: {audio_path}")
        transcribed_text = self.recommender.transcribe_audio(audio_path)

        if not transcribed_text:
            print("경고: 음성 인식에 실패했거나 텍스트가 없습니다. 추천을 진행할 수 없습니다.")
            return []

        print(f"\n인식된 텍스트: '{transcribed_text}'")

        # 단계 2: 텍스트 기반으로 음악 추천
        print("\n--- 단계 2: 음악 추천 생성 ---")
        recommendations = self.recommender.recommend_from_text(transcribed_text)

        if recommendations:
            print("\n--- 파이프라인 종료: 추천 목록 ---")
            for i, r in enumerate(recommendations, 1):
                print(f"{i}. {r}")
        else:
            print("\n--- 파이프라인 종료: 추천된 음악이 없습니다. ---")

        return recommendations
