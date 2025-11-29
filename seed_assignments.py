#!/usr/bin/env python3
"""
Seed sample assignment data for all 12 students.
Creates 3-4 assignments per student with various statuses and due dates.
"""

import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'learnmatrix')
)

cursor = conn.cursor()

# Fetch all student IDs and one teacher ID
cursor.execute("SELECT UserID FROM Users WHERE Role = 'Student' ORDER BY UserID LIMIT 12")
students = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT UserID FROM Users WHERE Role = 'Teacher' LIMIT 1")
teacher_result = cursor.fetchone()
teacher_id = teacher_result[0] if teacher_result else 1

# Fetch all exams
cursor.execute("SELECT ExamID, ExamName FROM Exams ORDER BY ExamID")
exams = cursor.fetchall()

if not exams:
    print("❌ No exams found. Please seed exams first with seed_db.py")
    cursor.close()
    conn.close()
    exit(1)

print(f"📚 Found {len(exams)} exams and {len(students)} students")
print(f"👨‍🏫 Using teacher ID: {teacher_id}")

# Assignment statuses and sample due dates
statuses = ['Assigned', 'Started', 'Completed', 'Overdue']
base_date = datetime.now()

assignments_created = 0

# Create assignments for each student
for student_idx, student_id in enumerate(students):
    # Assign 3-4 exams to each student with different statuses
    for exam_idx, (exam_id, exam_name) in enumerate(exams[:3]):
        # Vary due date based on status
        status_idx = (student_idx + exam_idx) % len(statuses)
        status = statuses[status_idx]
        
        if status == 'Assigned':
            due_date = base_date + timedelta(days=7)
        elif status == 'Started':
            due_date = base_date + timedelta(days=5)
        elif status == 'Completed':
            due_date = base_date - timedelta(days=2)
        else:  # Overdue
            due_date = base_date - timedelta(days=5)
        
        try:
            # Check if assignment already exists
            cursor.execute(
                "SELECT AssignmentID FROM Assignments WHERE TeacherID = %s AND StudentID = %s AND ExamID = %s",
                (teacher_id, student_id, exam_id)
            )
            existing = cursor.fetchone()
            
            if not existing:
                # Insert assignment
                cursor.execute(
                    """INSERT INTO Assignments (TeacherID, StudentID, ExamID, Status, DueDate)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (teacher_id, student_id, exam_id, status, due_date)
                )
                assignments_created += 1
                print(f"✅ Created: Student {student_id}, Exam {exam_name}, Status: {status}")
        except Exception as e:
            print(f"⚠️  Assignment exists or error: Student {student_id}, Exam {exam_name}: {e}")

conn.commit()
print(f"\n📊 Total assignments created: {assignments_created}")

cursor.close()
conn.close()

print("✅ Sample assignment data seeded successfully!")
