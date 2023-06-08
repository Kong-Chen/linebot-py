import psycopg2
import uuid
from psycopg2.extensions import adapt, register_adapter

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

    user_message='1wrwretwrg'
    user_nickname='Kong'
    user_id='111'
    cursor = connection.cursor()
    cursor.execute("INSERT INTO bot_user (user_id,user_name,line_id) VALUES (%s,%s,%s)", (uuid.uuid4(),user_nickname,user_id))
    connection.commit()
    cursor.close()
    connection.close()


except psycopg2.Error as e:
    print("資料庫錯誤:", e)

# 處理查詢結果
#for row in rows:
#    print(row)
