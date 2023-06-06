from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 設置你的 LINE Bot 的 Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi(os.environ['czH9a2VRdE4WY0n031h2sMjVEs979haELbdnS1QTvd8WooM7wMtulpBp1sTMqDua60W0Gq6M0oo+gH6hkcfAuyTiUFjq1Xrlhi+Pkts+9p9AsbdGNqAO2oGhK3AlGhZuf9NKV+QVtUTENFTWJG0wNAdB04t89/1O/w1cDnyilFU='])
handler = WebhookHandler(os.environ['cb67a671669fd689df93422edd6fea22'])


@app.route("/callback", methods=['POST'])
def callback():
    # 取得 request headers 中的 X-Line-Signature 屬性
    signature = request.headers['X-Line-Signature']
    
    # 取得 request 的 body 內容
    body = request.get_data(as_text=True)
    
    try:
        # 驗證簽章
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 收到使用者的訊息
    user_message = event.message.text
    
    # 回覆相同的訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=user_message)
    )

if __name__ == "__main__":
    app.run()