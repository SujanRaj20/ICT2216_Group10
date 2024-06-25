import pymysql

connection = pymysql.connect(
    host='3.145.129.7',
    user='root',
    password='kMcFNgtzJTA0{XW',
    db='bookwise',
    port=3306
)

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE();")
        result = cursor.fetchone()
        print("Connected to database:", result)
finally:
    connection.close()
