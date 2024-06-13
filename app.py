from flask import Flask, request, jsonify
from gptAssistant import ask_question
from io import BytesIO
from whisperSTT import transcribe_audio, load_audio
from flask_cors import CORS
from tts import play_tts

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB, 파일 크기 제한
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'
@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    바이너리 음성 데이터를 받아 텍스트로 변환하는 엔드포인트.
    """
    if not request.data:
        return jsonify({"error": "No data provided"}), 400
    try:
        # BytesIO 객체를 np.ndarray로 변환
        file_stream = BytesIO(request.data)
        file_stream.seek(0)
        audio = load_audio(file_stream)
        # 텍스트로 변환
        transcribed_text = transcribe_audio(audio)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"transcription": transcribed_text})

@app.route('/philosophy/<model>/<question>')
def ask_philosophy(model, question):
    response = ask_question(question, model)
    play_tts(response)
    return jsonify(response)


if __name__ == '__main__':
    app.run()
