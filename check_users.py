import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'learnmatrix'),
}

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Check student users
cursor.execute("SELECT UserID, Username, FirstName, Role FROM Users WHERE Role = 'Student' LIMIT 3")
students = cursor.fetchall()
print('Student Users:')
for s in students:
    print(f'  {s[1]} (ID: {s[0]}, Name: {s[2]})')

cursor.close()
conn.close()
