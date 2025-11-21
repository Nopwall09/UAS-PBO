import mysql.connector
def create_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        database="db_pbo_uas",
        password=""
    )
    return connection
def close_connection(connection):
    if connection.is_connected():
        connection.close()
