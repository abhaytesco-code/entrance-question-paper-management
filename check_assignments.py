#!/usr/bin/env python3
import mysql.connector
from config import db_config

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Check assignments
    cursor.execute('SELECT COUNT(*) FROM Assignments')
    count = cursor.fetchone()[0]
    print(f'Total Assignments: {count}')
    
    # List assignments
    if count > 0:
        cursor.execute('SELECT AssignmentID, TeacherID, StudentID, ExamID, Status, DueDate FROM Assignments LIMIT 5')
        print('\nSample Assignments:')
        for row in cursor.fetchall():
            print(f'  Assignment {row[0]}: Teacher {row[1]}, Student {row[2]}, Exam {row[3]}, Status: {row[4]}, Due: {row[5]}')
    
    # Check exams
    cursor.execute('SELECT COUNT(*) FROM Exams')
    exam_count = cursor.fetchone()[0]
    print(f'\nTotal Exams: {exam_count}')
    
    if exam_count > 0:
        cursor.execute('SELECT ExamID, ExamName FROM Exams LIMIT 5')
        print('Sample Exams:')
        for row in cursor.fetchall():
            print(f'  Exam {row[0]}: {row[1]}')
    
    # Check users
    cursor.execute('SELECT COUNT(*) FROM Users WHERE Role = "Student"')
    student_count = cursor.fetchone()[0]
    print(f'\nTotal Students: {student_count}')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')
