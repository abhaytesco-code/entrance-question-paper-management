"""
LearnMatrix: Personalized & Gamified Entrance Exam Learning System
Database Initialization Script
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'learnmatrix')
}

def initialize_database():
    """Initialize the LearnMatrix database with schema and sample data."""
    
    # Read the SQL schema file
    schema_file = 'learnmatrix_schema.sql'
    
    if not os.path.exists(schema_file):
        print(f"Error: {schema_file} not found!")
        return False
    
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"✓ Database '{DB_CONFIG['database']}' created/verified")
        
        # Switch to the database
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Read and execute SQL schema
        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
            # Split by semicolon and execute each statement
            statements = sql_content.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    try:
                        cursor.execute(statement)
                    except Error as err:
                        if "already exists" not in str(err):
                            print(f"⚠ Warning: {err}")
        
        connection.commit()
        print("✓ Database schema and sample data initialized successfully!")
        
        # Verify tables
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = %s
        """, (DB_CONFIG['database'],))
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✓ Created {len(tables)} tables: {', '.join(tables)}")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as err:
        print(f"✗ Database Error: {err}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("LearnMatrix Database Initialization")
    print("=" * 60)
    
    if initialize_database():
        print("\n✓ Database setup completed successfully!")
        print("\nYou can now start the Flask application with:")
        print("  python app.py")
    else:
        print("\n✗ Database initialization failed!")
        print("Please check your database configuration in .env")
