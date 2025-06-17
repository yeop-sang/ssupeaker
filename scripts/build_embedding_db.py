#!/usr/bin/env python3
import pickle
from pathlib import Path
import torch
from transformers import ClapModel, ClapProcessor
import librosa  # 오디오 파일 로드를 위해 librosa 추가
import argparse

# Helper function to load the model
def _load_clap_model(device):
    """CLAP 모델과 프로세서를 로드합니다."""
    print("Loading CLAP model...")
    # Using a smaller, faster model for demonstration
    model = ClapModel.from_pretrained(
        "laion/larger_clap_music", use_safetensors=True
    ).to(device)
    processor = ClapProcessor.from_pretrained("laion/larger_clap_music")
    print("CLAP model loaded successfully.")
    return model, processor

# Helper function to compute embedding
def _get_audio_embedding(audio_path, model, processor, device):
    """Computes a CLAP embedding for a single audio file."""
    # librosa를 사용해 오디오 파일을 로드하고 resample
    try:
        y, sr = librosa.load(audio_path, sr=48000)  # CLAP 모델은 48kHz 샘플링 레이트를 기대합니다.
    except Exception as e:
        print(f"Error loading audio file {audio_path}: {e}")
        return None

    audio_inputs = processor(audios=y, return_tensors="pt", padding=True, sampling_rate=48000)
    
    for key in audio_inputs:
        if isinstance(audio_inputs[key], torch.Tensor):
            audio_inputs[key] = audio_inputs[key].to(device)

    with torch.no_grad():
        audio_embedding = model.get_audio_features(**audio_inputs)
        
    return audio_embedding.cpu()

def build_embedding_database(music_dir_path: str, output_db_path: str):
    """
    Scans a directory of music files, computes their embeddings, and saves them to a database file.

    Args:
        music_dir_path (str): The path to the directory containing music files.
        output_db_path (str): The path where the embedding database file (.pkl) will be saved.
    """
    # 1. Device setup and model loading
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model, processor = _load_clap_model(device)

    # 2. Audio file scanning
    music_dir = Path(music_dir_path)
    if not music_dir.is_dir():
        print(f"Error: Provided music directory does not exist: {music_dir}")
        return

    print(f"Scanning for audio files in '{music_dir}'...")
    audio_files = list(music_dir.rglob("*.mp3")) + list(music_dir.rglob("*.wav"))
    print(f"총 {len(audio_files)}개의 오디오 파일을 찾았습니다.")

    # 3. Embedding computation
    embedding_data = []

    for audio_path in audio_files:
        try:
            abs_path_str = str(audio_path.resolve())
            print(f"Processing: {abs_path_str}")
            
            embedding_vector = _get_audio_embedding(abs_path_str, model, processor, device)
            
            if embedding_vector is not None:
                embedding_data.append((abs_path_str, embedding_vector))
        except Exception as e:
            print(f"Could not process file {audio_path}. Reason: {e}")
            continue

    print(f"총 {len(embedding_data)}개의 임베딩을 생성했습니다.")

    # 4. Save database file
    output_path = Path(output_db_path)
    output_path.parent.mkdir(parents=True, exist_ok=True) 

    print(f"'{output_path}'에 {len(embedding_data)}개의 항목을 저장합니다.")
    with open(output_path, 'wb') as f:
        pickle.dump(embedding_data, f)

    print(f"\n총 {len(embedding_data)}개의 임베딩이 데이터베이스에 저장되었습니다.")
    print(f"데이터베이스 저장 완료: '{output_path}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="음악 파일이 있는 디렉토리를 스캔하고, CLAP 임베딩을 계산한 후 데이터베이스 파일로 저장합니다."
    )
    parser.add_argument(
        "music_dir_path",
        type=str,
        help="음악 파일이 포함된 디렉토리의 경로입니다.",
    )
    parser.add_argument(
        "output_db_path",
        type=str,
        help="임베딩 데이터베이스 파일(.pkl)을 저장할 경로입니다.",
    )

    args = parser.parse_args()

    build_embedding_database(
        music_dir_path=args.music_dir_path, output_db_path=args.output_db_path
    )
