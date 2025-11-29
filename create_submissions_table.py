#!/usr/bin/env python3
"""Create AssignmentSubmissions table if it doesn't exist."""

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'learnmatrix')
)

cursor = conn.cursor()

sql = '''
CREATE TABLE IF NOT EXISTS AssignmentSubmissions (
    SubmissionID INT AUTO_INCREMENT PRIMARY KEY,
    AssignmentID INT NOT NULL,
    StudentID INT NOT NULL,
    FilePath VARCHAR(500) NOT NULL,
    FileName VARCHAR(255) NOT NULL,
    FileSize INT COMMENT "in bytes",
    SubmittedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Grade VARCHAR(2),
    TeacherFeedback LONGTEXT,
    GradedAt TIMESTAMP NULL,
    
    FOREIGN KEY (AssignmentID) REFERENCES Assignments(AssignmentID) ON DELETE CASCADE,
    FOREIGN KEY (StudentID) REFERENCES Users(UserID) ON DELETE CASCADE,
    
    INDEX idx_assignment_submissions (AssignmentID),
    INDEX idx_student_submissions (StudentID),
    INDEX idx_submitted_at (SubmittedAt),
    UNIQUE KEY unique_assignment_submission (AssignmentID, StudentID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
'''

try:
    cursor.execute(sql)
    conn.commit()
    print('✅ AssignmentSubmissions table created successfully')
except Exception as e:
    print(f'⚠️ Table exists or error: {e}')

cursor.close()
conn.close()
