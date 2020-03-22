from flask import Flask, request, jsonify
from telegram_bot import TelegramBot

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def index():
    req = request.get_json()
    bot = TelegramBot()
    success = bot.handle(req)
    return jsonify(success=success)


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(port=5000)
