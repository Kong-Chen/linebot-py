from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import uuid
from psycopg2.extensions import adapt, register_adapter
import psycopg2

app = Flask(__name__)

# 設置你的 LINE Bot 的 Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])


# 註冊 UUID 型別的適應器
def adapt_uuid(uuid):
    return adapt(str(uuid))
register_adapter(uuid.UUID, adapt_uuid)


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
    
    # 建立連接 (修改)
    connection = psycopg2.connect(
        host="dpg-ci01rn33cv20nhqqkd50-a.oregon-postgres.render.com",
        port="5432",
        database="linebot_trm4",
        user="kong",
        password="kmJreG7MV3OY8NYcVn9tNYHK3HhzCWBh"
    )
    
    # 收到使用者的訊息
    user_message = event.message.text
    user_line_id = event.source.user_id
    user_id = None
    user_nickname = None
    if event.source.type == 'user':
        profile = line_bot_api.get_profile(user_line_id)
        user_nickname = profile.display_name


    try:
 
        cursor = connection.cursor()     
        cursor.execute("SELECT user_id FROM bot_user WHERE line_id = %s", (user_line_id,))
        existing_user = cursor.fetchone()
        
        #判斷是否存在：不存在新增／存在則更新暱稱
        if existing_user:
            cursor.execute("UPDATE bot_user SET user_name = %s WHERE line_id = %s", (user_nickname, user_line_id))
            user_id = existing_user
        else:
            new_id = uuid.uuid4()
            cursor.execute("INSERT INTO bot_user (user_id, user_name, line_id) VALUES (%s, %s, %s)", (new_id, user_nickname, user_line_id))
            user_id = new_id 

        #新增對話
        cursor.execute("INSERT INTO bot_chat (user_id, chat_rank,chat_message,chat_time) VALUES (%s, %s, %s, %s)", (user_id,1,user_message,12345))

        connection.commit()
        cursor.close()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="正確寫入喔!!!!")
        )

    except psycopg2.Error as e:
        # print("資料庫錯誤:", e)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="資料庫錯誤啦!")
        )

    finally:
        connection.close()

if __name__ == "__main__":
    # 在本地運行時才啟動伺服器
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))