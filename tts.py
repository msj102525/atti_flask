# -*- coding: utf-8 -*-
import os
import urllib.request
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
from dotenv import load_dotenv
import base64

# .env 파일에서 환경 변수 로드
load_dotenv()


def play_tts(text, model):
    client_id = os.getenv('NAVER_CLIENT_ID').strip()
    client_secret = os.getenv('NAVER_CLIENT_SECRET').strip()

    # 모델별로 다른 목소리 설정
    if model == "socrates":
        speaker = "nyoungil"
    elif model == "descartes":
        speaker = "nminsang"
    else:
        speaker = "nminsang"  # 기본 값 설정

    encText = urllib.parse.quote(text)
    data = f"speaker={speaker}&volume=0&speed=0&pitch=0&format=mp3&text={encText}"
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)

    response = urllib.request.urlopen(request, data=data.encode('utf-8'))
    rescode = response.getcode()

    if rescode == 200:
        print("TTS mp3 변환 성공")
        response_body = response.read()
        print("TTS Response Body Length:", len(response_body))
        # Base64 인코딩
        response_base64 = base64.b64encode(response_body).decode('utf-8')
        return response_base64
    else:
        print("Error Code:" + str(rescode))
        return None