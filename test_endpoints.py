#!/usr/bin/env python3
"""
Smoke tests for LearnMatrix API endpoints.
Tests key endpoints without using the browser to catch API issues quickly.
"""

import os
import requests
import json

BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')
# Read test credentials from environment. If STUDENT user not set, student tests will be skipped.
STUDENT_USER = os.environ.get('TEST_STUDENT_USER')
TEACHER_USER = os.environ.get('TEST_TEACHER_USER', 'teacher_test')
PASSWORD = os.environ.get('TEST_PASSWORD', 'test123')

def log(message, level="INFO"):
    print(f"[{level}] {message}")

def test_health():
    """Test DB health endpoint"""
    log("Testing /api/db-health...")
    try:
        r = requests.get(f"{BASE_URL}/api/db-health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            log(f"✓ Health Check OK: {data}")
            return True
        else:
            log(f"✗ Health check failed with status {r.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"✗ Health check error: {e}", "ERROR")
        return False

def login(username, password):
    """Login and return session"""
    log(f"Logging in as {username}...")
    session = requests.Session()
    try:
        r = session.post(f"{BASE_URL}/login", json={
            "username": username,
            "password": password
        }, timeout=10)
        if r.status_code == 200:
            data = r.json()
            log(f"✓ Login successful: {data.get('message')}")
            return session
        else:
            log(f"✗ Login failed: {r.json()}", "ERROR")
            return None
    except Exception as e:
        log(f"✗ Login error: {e}", "ERROR")
        return None

def test_student_endpoints():
    """Test student API endpoints"""
    log("\n=== TESTING STUDENT ENDPOINTS ===")
    if not STUDENT_USER:
        log("Skipping student endpoint tests: TEST_STUDENT_USER not set", "WARN")
        return
    session = login(STUDENT_USER, PASSWORD)
    if not session:
        log("Cannot test student endpoints without login", "WARN")
        return
    
    endpoints = [
        "/api/student/stats",
        "/api/student/assignments",
        "/api/student/achievements",
        "/api/student/analytics",
        "/api/student/weakness-topics",
        "/api/student/class-stats"
    ]
    
    for endpoint in endpoints:
        try:
            r = session.get(f"{BASE_URL}{endpoint}", timeout=5)
            if r.status_code == 200:
                log(f"✓ {endpoint}")
            else:
                log(f"✗ {endpoint}: {r.status_code}", "WARN")
        except Exception as e:
            log(f"✗ {endpoint}: {e}", "ERROR")

def test_teacher_endpoints():
    """Test teacher API endpoints"""
    log("\n=== TESTING TEACHER ENDPOINTS ===")
    session = login(TEACHER_USER, PASSWORD)
    if not session:
        log("Cannot test teacher endpoints without login", "WARN")
        return
    
    endpoints = [
        "/api/teacher/stats",
        "/api/teacher/all-students",
        "/api/teacher/student-roster",
        "/api/teacher/class-analytics",
        "/api/teacher/assignments",
        "/api/admin/teachers"
    ]
    
    for endpoint in endpoints:
        try:
            r = session.get(f"{BASE_URL}{endpoint}", timeout=5)
            if r.status_code == 200:
                data = r.json()
                # Count items in response
                if isinstance(data, dict):
                    items = 0
                    for key in ['students', 'teachers', 'assignments', 'doubts']:
                        if key in data and isinstance(data[key], list):
                            items = len(data[key])
                            break
                    log(f"✓ {endpoint} ({items} items)")
                else:
                    log(f"✓ {endpoint}")
            else:
                log(f"✗ {endpoint}: {r.status_code}", "WARN")
        except Exception as e:
            log(f"✗ {endpoint}: {e}", "ERROR")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("LearnMatrix API Endpoint Smoke Tests")
    print("="*60 + "\n")
    
    test_health()
    test_student_endpoints()
    test_teacher_endpoints()
    
    print("\n" + "="*60)
    print("Tests Complete!")
    print("="*60 + "\n")
