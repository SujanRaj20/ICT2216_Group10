import mysql.connector

def get_mysql_connection():
    try:
        # Replace with your MySQL connection details
        conn = mysql.connector.connect(
            host='172.21.0.2',
            user='root',
            password='***REMOVED***',
            database='***REMOVED***'
        )
        print("MySQL connection established successfully")
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None
