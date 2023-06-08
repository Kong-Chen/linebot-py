import psycopg2

# 建立連線
try:
    connection = psycopg2.connect(
        host="dpg-ci01rn33cv20nhqqkd50-a.oregon-postgres.render.com",
        port="5432",
        database="linebot_trm4",
        user="kong1229",
        password="kmJreG7MV3OY8NYcVn9tNYHK3HhzCWBh",
        sslmode="require"
    )
    print("資料庫錯誤正確")
    """
    user_message='1wrwretwrg'
    cursor = connection.cursor()
    cursor.execute("INSERT INTO word (word_desc) VALUES (%s)", (user_message,))
    connection.commit()
    cursor.close()
    connection.close()
    """

except psycopg2.Error as e:
    print("資料庫錯誤:", e)

# 處理查詢結果
#for row in rows:
#    print(row)
