import os
import json
import random
from typing import List, Dict, cast
import whisper
import torch

class AudioRecommender:
    whisper_model: whisper.Whisper
    device: str
    music_tags: Dict[str, List[str]]

    def __init__(self, whisper_model_size="base", device=None):
        """
        Initialize the AudioRecommender with a Whisper model.
        The recommendation logic is now based on keyword-tag matching.

        Args:
            whisper_model_size (str): Size of the Whisper model to use.
            device (str): Device to run models on ('cuda' or 'cpu').
        """
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"Using device: {self.device}")

        print(f"Loading Whisper model ({whisper_model_size})...")
        self.whisper_model = whisper.load_model(whisper_model_size)
        self.whisper_model = self.whisper_model.to(self.device)

        print("Loading music tags...")
        try:
            with open("tags.json", "r", encoding="utf-8") as f:
                self.music_tags = json.load(f)
        except FileNotFoundError:
            print("Error: tags.json not found. Please create it in the project root.")
            self.music_tags = {}
        except json.JSONDecodeError:
            print("Error: tags.json is not a valid JSON file.")
            self.music_tags = {}

    def recommend_from_text(self, text: str) -> List[str]:
        """
        Recommends music based on keywords found in the text.
        (Temporarily modified to return random recommendations)

        Args:
            text (str): The input text (e.g., from speech-to-text).

        Returns:
            A list of recommended music file names.
        """
        # --- 기존 키워드 기반 추천 로직 (임시 주석 처리) ---
        # sad_keywords = ['이별', '헤어지자', '슬퍼', '슬픔', '눈물']
        # happy_keywords = ['파티', '신난다', '행복', '즐거움', '기쁨', '축하']
        #
        # recommended_music = []
        # text_lower = text.lower()
        #
        # found_sad = any(keyword in text_lower for keyword in sad_keywords)
        # found_happy = any(keyword in text_lower for keyword in happy_keywords)
        #
        # target_tags = set()
        # if found_sad:
        #     print("Detected sad keywords.")
        #     target_tags.update(['슬픔', '차분함'])
        #
        # if found_happy:
        #     print("Detected happy keywords.")
        #     target_tags.update(['밝음', '즐거움', '신남'])
        #
        # if not target_tags:
        #     print("No specific keywords found, recommending neutral music.")
        #     target_tags.add('중립')
        #
        # for music_file, tags in self.music_tags.items():
        #     if any(tag in tags for tag in target_tags):
        #         recommended_music.append(music_file)
        #
        # return recommended_music

        # --- 임시 랜덤 추천 로직 ---
        print("Using temporary random recommendation logic.")
        all_music = list(self.music_tags.keys())
        if not all_music:
            return []
        
        num_to_recommend = min(len(all_music), 3)
        
        return random.sample(all_music, num_to_recommend)

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribes the given audio file to text using Whisper.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            The transcribed text.
        """
        print(f"오디오 파일의 음성을 텍스트로 변환합니다: {audio_path}")
        try:
            result = self.whisper_model.transcribe(audio_path, fp16=torch.cuda.is_available())
            text = cast(str, result.get("text", ""))
            print("음성 변환 완료.")
            return text
        except Exception as e:
            print(f"오류: 음성 변환 중 예외 발생 - {e}")
            return ""
