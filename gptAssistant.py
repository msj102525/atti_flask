from openai import OpenAI
import time
import re
import os
from dotenv import load_dotenv

# 발급받은 API 키 설정
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def ask_question(question, model):
    # 새로운 스레드 생성
    thread = client.beta.threads.create()
    # assistantModel = {"schopenhauer": "asst_ZQKG1uvM81IcDZXjocWeayWU",
    #                "descartes": "asst_w5bzDa5z6WkvhXmUNM7tcVr1",
    #                   "socrates": "asst_PGnZCOkyXYt4I75LKG1lZXVz",
    #                   "aristotle": "asst_66gquf4MpkCmvNDphwmVIZ4z",
    #                   "confucius": "asst_7HdBohy9jnXtoxF1w8CWj3g5",
    #                   "plato": "asst_zhOklyn0xmH6LhcdyAyjID5X"}
    # assistantId = assistantModel[model]
    
    
    
    #배포 전까지 테스트 모델 사용
    assistantId="asst_66gquf4MpkCmvNDphwmVIZ4z"


    # 사용자 메시지 전송

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question,
    )
    # assistant로 실행 생성
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistantId,
    )
    # 실행 완료까지 대기
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    # 스레드의 메시지 응답 가져오기
    response = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    # 'assistant'의 메시지 찾기
    response_message = None
    print(response)
    for res in response:
        if res.role.lower() == 'assistant':
            response_message = res.content[0].text.value
            break
    if response_message is None:
        return "No response from assistant."
    # 데이터 줄바꿈 및 인용구 제거
    print(response_message)
    clean_text = re.sub(r'【\d+:\d+†source】', '', response_message)
    clean_text = re.sub(r'\n', ' ', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text
