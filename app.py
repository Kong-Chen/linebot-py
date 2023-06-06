from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['k0sIodOhhK839szfy08KD17qvPNWZWxmYhogR+HLGnEMoK14IEMwsT5F6VXQ//4N60W0Gq6M0oo+gH6hkcfAuyTiUFjq1Xrlhi+Pkts+9p/A1aGl94FMHut2rIxJ8hrrCHxQIXRVzoYUKDVaKIeIPAdB04t89/1O/w1cDnyilFU='])
handler = WebhookHandler(os.environ['0c3568a19560c3b4757950de20b72f17'])


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK~'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
