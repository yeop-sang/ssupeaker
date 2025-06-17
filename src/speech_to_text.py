# Whisper 라이브러리를 불러옵니다
import whisper

# import mac_settings
import os


class SpeechToText:
    def __init__(self, model_size="base", device=None):
        """
        Initializes the Whisper model.

        Args:
            model_size (str): The size of the Whisper model to use (e.g., 'tiny', 'base').
            device (str): The device to run the model on ('cuda' or 'cpu').
        """
        print(f"Loading Whisper model ({model_size})...")
        self.model = whisper.load_model(model_size, device=device)
        print("Whisper model loaded.")

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes an audio file to text.

        Args:
            audio_path (str): The path to the audio file.

        Returns:
            str: The transcribed text.
        """
        print(f"Transcribing {audio_path}...")
        try:
            result = self.model.transcribe(audio_path)
            transcribed_text = result["text"]
            print(f"Transcription complete.")
            return transcribed_text
        except Exception as e:
            print(f"Error during transcription: {e}")
            return ""


if __name__ == "__main__":
    # This is an example of how to use the class.
    # It requires a sample audio file to run.
    # Create a dummy file for demonstrating the structure.
    # For a real test, replace with a valid audio file path.

    # Let's assume an audio file exists at 'example/audio_2_ko.mp3' for the example.
    example_audio_path = "example/audio_2_ko.mp3"

    if os.path.exists(example_audio_path):
        print("\n--- Testing SpeechToText class ---")
        stt = SpeechToText(model_size="tiny")  # Use 'tiny' for faster testing
        transcribed_text = stt.transcribe(example_audio_path)

        if transcribed_text:
            print(f"\nTranscribed Text:\n---\n{transcribed_text}\n---")
        else:
            print("\nTranscription failed or returned empty text.")
        print("\n--- Test finished ---")
    else:
        print(
            f"\nSkipping SpeechToText example because the audio file was not found: {example_audio_path}"
        )
        print("Please place a test audio file at that location to run the example.")
