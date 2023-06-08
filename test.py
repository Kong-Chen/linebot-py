import psycopg2
import uuid
from psycopg2.extensions import adapt, register_adapter
from datetime import datetime

# 註冊 UUID 型別的適應器
def adapt_uuid(uuid):
    return adapt(str(uuid))

register_adapter(uuid.UUID, adapt_uuid)


# 建立連線
try:
    connection = psycopg2.connect(
        host="dpg-ci01rn33cv20nhqqkd50-a.oregon-postgres.render.com",
        port="5432",
        database="linebot_trm4",
        user="kong",
        password="kmJreG7MV3OY8NYcVn9tNYHK3HhzCWBh",
        sslmode="require"
    )
    timestamp = datetime.now()
    user_message='8888888888'
    user_line_id='1111111'
    user_nickname='Kong'
    user_id='111'
    cursor = connection.cursor()

 
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
    cursor.execute("INSERT INTO bot_chat (user_id, chat_rank,chat_message,chat_time) VALUES (%s, %s, %s, %s)", (user_id,1,user_message,timestamp))


    
    
    connection.commit()
    cursor.close()
    connection.close()


except psycopg2.Error as e:
    print("資料庫錯誤:", e)

# 處理查詢結果
#for row in rows:
#    print(row)
