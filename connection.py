import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(host='localhost',
                                   database='thesis',
                                   user='root',
                                   password='')
    print("Connection ok.")

except Error as e:
    print('Error', e)