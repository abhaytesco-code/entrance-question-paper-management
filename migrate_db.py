"""
Database migration script to add ImagePath column to Doubts table
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'learnmatrix')
    )
    
    cursor = conn.cursor()
    
    # Check if ImagePath column already exists
    cursor.execute("""
        SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME='Doubts' AND COLUMN_NAME='ImagePath'
    """)
    
    if not cursor.fetchone():
        print("Adding ImagePath column to Doubts table...")
        cursor.execute("""
            ALTER TABLE Doubts ADD COLUMN ImagePath VARCHAR(255) AFTER DoubtText
        """)
        conn.commit()
        print("✓ ImagePath column added successfully")
    else:
        print("✓ ImagePath column already exists")
    
    cursor.close()
    conn.close()
    print("\nDatabase migration completed!")
    
except Error as err:
    print(f"Error: {err}")
