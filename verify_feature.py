#!/usr/bin/env python3
"""
Verification script for Assignment Submission Feature
Checks that all components are properly installed and configured.
"""

import os
import mysql.connector
from dotenv import load_dotenv
import sys

def check_mark(status):
    return "[OK]" if status else "[FAIL]"

print("=" * 60)
print("ASSIGNMENT SUBMISSION FEATURE - VERIFICATION")
print("=" * 60)

# Load environment
load_dotenv()

# 1. Check files exist
print("\n1. CHECKING FILES...")
files_to_check = [
    "app.py",
    "templates/student/assignments.html",
    "templates/teacher/assignments.html",
    "learnmatrix_schema.sql",
    "seed_assignments.py",
]

all_files_exist = True
for file in files_to_check:
    exists = os.path.exists(file)
    print(f"   {check_mark(exists)} {file}")
    all_files_exist = all_files_exist and exists

# 2. Check database connectivity
print("\n2. CHECKING DATABASE...")
try:
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'learnmatrix')
    }
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print(f"   ✅ Database connection successful")
    
    # Check AssignmentSubmissions table
    cursor.execute("SHOW TABLES LIKE 'AssignmentSubmissions'")
    has_table = cursor.fetchone() is not None
    print(f"   {check_mark(has_table)} AssignmentSubmissions table exists")
    
    # Check data
    cursor.execute("SELECT COUNT(*) FROM Assignments")
    assignment_count = cursor.fetchone()[0]
    print(f"   ✅ Total assignments: {assignment_count}")
    
    cursor.execute("SELECT COUNT(*) FROM Users WHERE Role = 'Student'")
    student_count = cursor.fetchone()[0]
    print(f"   ✅ Total students: {student_count}")
    
    cursor.execute("SELECT COUNT(*) FROM Users WHERE Role = 'Teacher'")
    teacher_count = cursor.fetchone()[0]
    print(f"   ✅ Total teachers: {teacher_count}")
    
    cursor.execute("SELECT COUNT(*) FROM Exams")
    exam_count = cursor.fetchone()[0]
    print(f"   ✅ Total exams: {exam_count}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Database error: {e}")
    sys.exit(1)

# 3. Check uploads directory
print("\n3. CHECKING UPLOADS DIRECTORY...")
uploads_path = os.path.join("uploads", "submissions")
exists = os.path.exists(uploads_path) or os.path.exists("uploads")
print(f"   {check_mark(exists)} uploads directory exists or will be created on first upload")

# 4. Check Python imports
print("\n4. CHECKING PYTHON IMPORTS...")
imports_to_check = [
    ("flask", "Flask"),
    ("mysql.connector", "MySQL Connector"),
    ("werkzeug.utils", "Werkzeug Utils"),
    ("dotenv", "Python dotenv"),
]

all_imports_ok = True
for module, name in imports_to_check:
    try:
        __import__(module)
        print(f"   ✅ {name} ('{module}')")
    except ImportError:
        print(f"   ❌ {name} ('{module}') - NOT INSTALLED")
        all_imports_ok = False

# 5. Check app.py for endpoints
print("\n5. CHECKING API ENDPOINTS IN app.py...")
with open("app.py", "r") as f:
    app_content = f.read()

endpoints_to_check = [
    ("/api/submit-assignment", "Student file upload"),
    ("/api/student/submissions", "Student view submissions"),
    ("/api/teacher/submissions", "Teacher view submissions"),
    ("/api/grade-submission", "Teacher grade submission"),
    ("/uploads/submissions", "File download endpoint"),
]

all_endpoints_ok = True
for endpoint, description in endpoints_to_check:
    exists = endpoint in app_content
    print(f"   {check_mark(exists)} {endpoint} - {description}")
    all_endpoints_ok = all_endpoints_ok and exists

# 6. Check templates for components
print("\n6. CHECKING UI TEMPLATES...")

# Student template
with open("templates/student/assignments.html", "r") as f:
    student_content = f.read()

student_checks = [
    ("Pending Assignments", "Pending assignments tab"),
    ("Submitted Assignments", "Submitted assignments tab"),
    ("submitAssignment", "File upload function"),
]

print("   Student Template:")
for check_str, description in student_checks:
    exists = check_str in student_content
    print(f"      {check_mark(exists)} {description}")

# Teacher template
with open("templates/teacher/assignments.html", "r") as f:
    teacher_content = f.read()

teacher_checks = [
    ("View Submissions", "View submissions tab"),
    ("gradingModal", "Grading modal"),
    ("submitGrade", "Grade submission function"),
]

print("   Teacher Template:")
for check_str, description in teacher_checks:
    exists = check_str in teacher_content
    print(f"      {check_mark(exists)} {description}")

# Final summary
print("\n" + "=" * 60)
print("VERIFICATION SUMMARY")
print("=" * 60)

print("\n✅ All Components Ready!" if all_files_exist and all_imports_ok and all_endpoints_ok else "\n⚠️  Some components may need attention")

print("\nNext Steps:")
print("1. Start Flask: python app.py")
print("2. Open browser: http://127.0.0.1:5000")
print("3. Follow QUICK_TEST_GUIDE.md for testing")

print("\nDocumentation:")
print("- FEATURE_COMPLETE.md - Feature summary")
print("- QUICK_TEST_GUIDE.md - Testing instructions")
print("- ASSIGNMENT_SUBMISSION_FEATURE.md - Technical details")

print("\n" + "=" * 60)
