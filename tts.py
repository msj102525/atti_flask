# -*- coding: utf-8 -*-
import os
import urllib.request
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()


def play_tts(text):
    client_id = os.getenv('NAVER_CLIENT_ID')
    client_secret = os.getenv('NAVER_CLIENT_SECRET')

    encText = urllib.parse.quote(text)
    data = f"speaker=nminsang&volume=0&speed=0&pitch=0&format=mp3&text={encText}"
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)

    response = urllib.request.urlopen(request, data=data.encode('utf-8'))
    rescode = response.getcode()
    if rescode == 200:
        print("TTS mp3 재생")
        response_body = response.read()

        # MP3 데이터를 AudioSegment로 변환
        audio = AudioSegment.from_file(BytesIO(response_body), format="mp3")

        # 오디오 재생
        play(audio)
    else:
        print("Error Code:" + str(rescode))


