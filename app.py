from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import uuid
from psycopg2.extensions import adapt, register_adapter
import psycopg2
from datetime import datetime

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
    timestamp = datetime.now()
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
        #cursor = connection.cursor() 
        cursor.execute("SELECT MAX(chat_rank) FROM bot_chat WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            chat_rank = result[0] + 1
        else:
            chat_rank = 1
        #cursor = connection.cursor() 
        cursor.execute("INSERT INTO bot_chat (user_id, chat_rank, chat_message, chat_time) VALUES (%s, %s, %s, %s)", (user_id, chat_rank, user_message, timestamp)) 
        #connection.commit() #爭議Kong
        
        # 特殊功能
        #cursor = connection.cursor() 
        cursor.execute("SELECT special_function FROM bot_parameter")
        is_special_function = cursor.fetchone()
        special_function = is_special_function[0]
        push_user_id = None
        push_user_line_id = None
        keyword = None
        result_user_id = None

        if special_function == True:
            #撈出使用者代碼
            #cursor = connection.cursor() 
            cursor.execute("SELECT user_id  FROM bot_user WHERE line_id = %s", (user_line_id,))
            result = cursor.fetchone()

            if result:
                #cursor = connection.cursor() 
                cursor.execute("SELECT sub_user_id  FROM bot_user_relation WHERE main_user_id = %s AND action_key = %s" , (result,user_message,))
                result_user_id = cursor.fetchone()
                if result_user_id:
                    push_user_id = result_user_id[0]
                    keyword = user_message

                else:
                    #cursor = connection.cursor() 
                    cursor.execute("SELECT main_user_id  FROM bot_user_relation WHERE sub_user_id  = %s AND action_key = %s", (result,user_message,))
                    result_user_id = cursor.fetchone()
                    if result_user_id:
                        push_user_id = result_user_id[0]
                        keyword = user_message
        
            if push_user_id is not None and keyword is not None:
                #取出關係人對話  
                #cursor = connection.cursor() 
                cursor.execute("SELECT chat_message  FROM bot_chat WHERE user_id = %s AND chat_message <> %s AND is_read=false Order by chat_rank" , (push_user_id,user_message,))
                result_chat_rows = cursor.fetchall()
                result_chat_all = "尚未讀取對話："+"\n"
                for result_chat_row in result_chat_rows:
                    result_chat_all += result_chat_row[0]+"\n"
                    #PUSH # 更新資料庫=1
                    cursor.execute("UPDATE bot_chat SET is_read=true WHERE user_id = %s AND chat_message = %s AND is_read=false " , (push_user_id,result_chat_row[0],))

                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=result_chat_all)
                )

            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你的訊息對話有收到喔!push_user_id is not None and keyword is not None")
                )
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你的訊息對話有收到喔!special_function")
        )
        cursor.close()
        connection.commit()
  

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