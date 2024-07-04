from flask import Flask, request, jsonify, send_file
from gptAssistant import ask_question
from io import BytesIO
from whisperSTT import transcribe_audio, load_audio
from flask_cors import CORS
from tts import play_tts
from sentiment import analyze_sentiment
import base64
import requests
from bs4 import BeautifulSoup
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy as sp

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
    audio_base64 = play_tts(response, model)
    response_json = {
        'text': response,
        'audio': audio_base64
    }
    return jsonify(response_json)


@app.route('/sentiment', methods=['POST'])
def sentiment():
    content = request.get_json().get('content')
    result = analyze_sentiment(content)
    print('sentiment : ', result)
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


######################################## 유사도
@app.route('/feed/similar/<int:feedNum>', methods=['GET'])
def similar_feeds(feedNum):
    auth_token = request.headers.get('Authorization')

    spring_boot_url = f'http://localhost:8080/feed/similar/{feedNum}'

    headers = {'Authorization': auth_token}
    response = requests.get(spring_boot_url, headers=headers)
    # print(f"Response status code: {response.status_code}")

    okt = Okt()
    vectorizer = TfidfVectorizer(min_df=1, decode_error='ignore')

    parseContents = []

    if response.status_code == 200:
        similar_feeds = response.json()

        for feed in similar_feeds:
            soup = BeautifulSoup(feed['feedContent'], "html.parser")
            feed_content = soup.get_text()
            parseContents.append(feed_content)

        # print(parseContents)

        # 토큰화
        contents_tokens = [okt.morphs(row) for row in parseContents]
        contents_for_vectorize = [' '.join(content) for content in contents_tokens]

        # tf-idf 벡터화
        X = vectorizer.fit_transform(contents_for_vectorize)
        num_samples, num_features = X.shape
        # print(num_samples, num_features)

        new_content = parseContents[0]
        print(f'비교할 대상: {new_content}')

        new_content_tokens = okt.morphs(new_content)
        new_content_for_vectorize = [' '.join(new_content_tokens)]

        new_content_vec = vectorizer.transform(new_content_for_vectorize)

        # 유사도 검사
        distances = []

        best_dist = float('inf')
        best_i = None

        for i in range(len(parseContents)):
            if i == 0:
                continue

            post_vec = X.getrow(i)

            # 함수 호출
            d = dist_raw(post_vec, new_content_vec)

            # print(f'==Post {similar_feeds[i]['feedNum']} with dis={d:.2f} : {parseContents[i]}')

            distances.append((i, d))

            if d == 0.00:
                continue

            if d < best_dist:
                best_dist = d
                best_i = i

        print(f'Best content is {best_i}, dist = {best_dist:.2f}')
        print('-->', new_content)
        print('--->', parseContents[best_i])

        # 유사도가 낮은 순서대로 정렬
        distances.sort(key=lambda x: x[1])

        # 최대 10개의 가장 유사한 피드를 선택
        similar_feeds_reordered = [similar_feeds[i[0]] for i in distances[1:11]]

        return jsonify(similar_feeds_reordered)

    else:
        print("Failed to retrieve similar feeds from Spring Boot server")
        return jsonify({"error": "Failed to retrieve similar feeds"}), 500


def dist_raw(v1, v2):
    delta = v1 - v2
    return sp.linalg.norm(delta.toarray())


# if __name__ == '__main__':
#     app.run()
