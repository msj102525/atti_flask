import whisper
import os


def transcribe_audio(audio_path, model_size="base"):
    """
    음성 파일을 텍스트로 변환하는 함수.

    Parameters:
    - audio_path (str): 변환할 음성 파일의 경로.
    - model_size (str): 사용할 Whisper 모델의 크기. 기본값은 "base".

    Returns:
    - str: 변환된 텍스트.
    """
    # 모델 로드 (CPU에서 실행)
    model = whisper.load_model(model_size, device="cpu")

    # 음성 파일을 텍스트로 변환
    result = model.transcribe(audio_path)

    # 변환된 텍스트 반환
    return result['text']


# 예제 사용

example_audio_path = "./audio/sample1.wav"
transcribed_text = transcribe_audio(example_audio_path)
print(transcribed_text)
