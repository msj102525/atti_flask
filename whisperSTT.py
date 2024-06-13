import whisper
import subprocess
import numpy as np
def load_audio(file, sr=16000):
    process = subprocess.Popen(
        ['ffmpeg', '-i', 'pipe:0', '-f', 'wav', '-acodec', 'pcm_s16le', '-ar', str(sr), '-ac', '1', 'pipe:1'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = process.communicate(input=file.read())
    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg 오류: {err.decode()}")
    # Load audio into numpy array
    audio = np.frombuffer(out, np.int16).astype(np.float32) / 32768.0  # Normalize to [-1, 1]
    return audio

def transcribe_audio(audio, model_size="base"):
    model = whisper.load_model(model_size, device="cpu")
    # Whisper expects a numpy array as input
    result = model.transcribe(audio)
    print(result)
    return result['text']