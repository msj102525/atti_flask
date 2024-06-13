from flask import Flask, jsonify
from gptAssistant import ask_question
from tts import play_tts

app = Flask(__name__)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/philosophy/<model>/<question>')
def ask_philosophy(model, question):
    response = ask_question(question, model)

    play_tts(response)

    return jsonify(response)

if __name__ == '__main__':
    app.run()
