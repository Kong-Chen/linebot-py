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
    user_message='繼續'
    keyword='繼續'
    user_line_id='1111111'
    user_nickname='測試'
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


    ########
    cursor.execute("SELECT user_id  FROM bot_user WHERE line_id = %s", (user_line_id,))
    result = cursor.fetchone()
    print("第一個" + result[0])  # Kong
    if result:
        cursor.execute("SELECT sub_user_id  FROM bot_user_relation WHERE main_user_id = %s AND action_key = %s" , (result,user_message,))
        result_user_id = cursor.fetchone()
        #print("第二個" + result_user_id[0])  # Kong
        if result_user_id:
            push_user_id = result_user_id
        else:
            cursor.execute("SELECT main_user_id  FROM bot_user_relation WHERE sub_user_id  = %s AND action_key = %s", (result,user_message,))
            push_user_id = cursor.fetchone()
        
        if push_user_id is not None and keyword is not None:
            #取出關係人對話  
            cursor.execute("SELECT chat_message  FROM bot_chat WHERE user_id = %s AND chat_message <> %s AND is_read=false Order by chat_rank" , (push_user_id,user_message,))
            result_chat_rows = cursor.fetchall()
            result_chat_all = None
            result_chat_all = "尚未讀取對話："+"\n"
            for result_chat_row in result_chat_rows:
                result_chat_all += result_chat_row[0]+"\n"
            print (result_chat_all)
            

    
    connection.commit()
    cursor.close()
    connection.close()


except psycopg2.Error as e:
    print("資料庫錯誤:", e)

# 處理查詢結果
#for row in rows:
#    print(row)
