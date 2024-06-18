from flask import Flask, request, jsonify, send_file
from gptAssistant import ask_question
from io import BytesIO
from whisperSTT import transcribe_audio, load_audio
from flask_cors import CORS
from tts import play_tts
from sentiment import analyze_sentiment
import base64

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB, 파일 크기 제한
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'
@app.route('/transcribe', methods=['POST'])
def transcribe():
    print("데이터 전송받음 !!!!!!!!!!!!!!!!!!!!")
    if 'file' not in request.files:
        return jsonify({"transcription": "No file provided"}), 400
    try:
        # BytesIO 객체를 np.ndarray로 변환
        file = request.files['file']
        print("file 잘와씀")
        file_stream = BytesIO(file.read())
        file_stream.seek(0)
        audio = load_audio(file_stream)
        # 텍스트로 변환
        transcribed_text = transcribe_audio(audio)
        print(transcribed_text)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"transcription": transcribed_text})

@app.route('/philosophy/<model>/<question>')
def ask_philosophy(model, question):
    response = ask_question(question, model)
    audio_base64=play_tts(response)
    response_json = {
        'text': response,
        'audio': audio_base64
    }
    return jsonify(response_json)


@app.route('/sentiment/<content>')
def sentiment(content):
    result = analyze_sentiment(content)
    print(result)
    return jsonify(result)

@app.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    audio_data = play_tts(text)
    if audio_data:
        encoded_audio = base64.b64encode(audio_data).decode('utf-8')
        return jsonify({"audio": encoded_audio})
    else:
        return jsonify({"error": "TTS 변환 실패"}), 500



if __name__ == '__main__':
    app.run()
