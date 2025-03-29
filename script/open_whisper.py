# Whisper 라이브러리를 불러옵니다
import whisper
# import mac_settings

# "audio.wav" 파일을 로드, "base" 크기의 whisper 모델을 불러옵니다
model = whisper.load_model("base")

# 모델의 transcribe 메소드를 사용하여 "audio_1.mp3" 파일을 텍스트로 변환합니다
# 이 메소드는 전체 파일을 읽고 30초 길이의 윈도우를 이동시키며 오디오를 처리합니다
# 각 윈도우에서 자동 회귀 시퀀스-투-시퀀스 예측을 수행합니다.
result = model.transcribe("example/audio_2_ko.mp3")
print(result['text'])

