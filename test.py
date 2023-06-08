import psycopg2

# 建立連線
connection = psycopg2.connect(
    host="dpg-ci01rn33cv20nhqqkd50-a.oregon-postgres.render.com",
    port="5432",
    database="linebot_trm4",
    user="kong",
    password="kmJreG7MV3OY8NYcVn9tNYHK3HhzCWBh",
    sslmode="require"
)

# 建立游標
cursor = connection.cursor()

# 執行 SQL 查詢
user_message='11112142r'
cursor = connection.cursor()
cursor.execute("INSERT INTO word (word_desc) VALUES (%s)", (user_message,))
connection.commit()
cursor.close()
connection.close()
# rows = cursor.fetchall()



# 處理查詢結果
#for row in rows:
#    print(row)
