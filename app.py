"""
LearnMatrix: Personalized & Gamified Entrance Exam Learning System
Flask Backend Application with Complete Routing Logic
Author: AI Code Generation System
Date: November 18, 2025
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
try:
    from flask_session import Session  # type: ignore
    _HAS_FLASK_SESSION = True
except Exception:
    # If flask-session is not installed or fails to import (native build deps),
    # fall back to Flask's default cookie sessions. This keeps the app runnable
    # in environments without C build tools.
    Session = None
    _HAS_FLASK_SESSION = False
from functools import wraps
import mysql.connector
from mysql.connector import Error
import bcrypt
import json
from datetime import datetime, timedelta
import os
import time
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize session management
if _HAS_FLASK_SESSION and Session is not None:
    Session(app)
else:
    # Fall back to Flask's signed cookie sessions when flask-session is unavailable.
    print('Warning: flask-session not available; using default cookie sessions.')

# Database connection configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'learnmatrix'),
    'autocommit': True
}

# ============================================================================
# DATABASE CONNECTION UTILITY
# ============================================================================
def get_db_connection():
    """Establish and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as err:
        if err.errno == 2003:
            print("Error: Unable to connect to MySQL Server.")
        elif err.errno == 1045:
            print("Error: Invalid username or password.")
        else:
            print(f"Error: {err}")
        return None

# Health check endpoint for quick DB/service verification
@app.route('/api/db-health')
def db_health():
    """Simple health check that verifies DB connectivity."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'db': 'unreachable'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        return jsonify({'status': 'ok', 'db': 'reachable'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'db_error': str(e)}), 500
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

# ============================================================================
# AUTHENTICATION DECORATORS & UTILITIES
# ============================================================================
def login_required(f):
    """Decorator to check if user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # If this is an API/XHR request, return JSON 401 instead of HTML redirect
            try:
                is_api = request.path.startswith('/api/') or request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            except Exception:
                is_api = False
            if is_api:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    """Decorator to check user role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                try:
                    is_api = request.path.startswith('/api/') or request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
                except Exception:
                    is_api = False
                if is_api:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('login'))
            if session.get('role') != role:
                return jsonify({'error': 'Unauthorized access'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def hash_password(password):
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================
@app.route('/', methods=['GET'])
def index():
    """Home/Landing page."""
    if 'user_id' in session:
        if session['role'] == 'Student':
            return redirect(url_for('student_dashboard'))
        elif session['role'] == 'Teacher':
            return redirect(url_for('teacher_dashboard'))
    return redirect(url_for('login'))

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve uploaded files."""
    return send_from_directory(os.path.join(os.getcwd(), 'uploads'), filename)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'Student')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()

        # Validation
        if not all([username, email, password, role]):
            return jsonify({'error': 'Missing required fields'}), 400

        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT UserID FROM Users WHERE Username = %s OR Email = %s", (username, email))
            if cursor.fetchone():
                return jsonify({'error': 'Username or email already exists'}), 400

            # Hash password and insert user
            password_hash = hash_password(password)
            cursor.execute(
                """INSERT INTO Users (Username, Email, PasswordHash, Role, FirstName, LastName)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (username, email, password_hash, role, first_name, last_name)
            )
            conn.commit()

            return jsonify({'message': 'Registration successful! Please login.'}), 201

        except Error as err:
            return jsonify({'error': f'Database error: {err}'}), 500
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route with session management."""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        # Accept either username or email for login to be more flexible
        username = (data.get('username') or data.get('email') or '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'error': 'Username/email and password required'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            cursor = conn.cursor()
            # Support login by username or email
            cursor.execute(
                "SELECT UserID, PasswordHash, Role, FirstName, LastName FROM Users WHERE Username = %s OR Email = %s",
                (username, username)
            )
            user = cursor.fetchone()

            if not user or not verify_password(password, user[1]):
                return jsonify({'error': 'Invalid username or password'}), 401

            # Update last login
            cursor.execute(
                "UPDATE Users SET LastLogin = NOW() WHERE UserID = %s",
                (user[0],)
            )
            conn.commit()

            # Create session
            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[2]
            session['first_name'] = user[3]
            session['last_name'] = user[4]

            return jsonify({
                'message': 'Login successful',
                'redirect': url_for('student_dashboard') if user[2] == 'Student' else url_for('teacher_dashboard')
            }), 200

        except Error as err:
            return jsonify({'error': f'Database error: {err}'}), 500
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout route."""
    session.clear()
    return redirect(url_for('login'))

# ============================================================================
# STUDENT PORTAL ROUTES
# ============================================================================
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student dashboard with personalized widgets."""
    return render_template('student/dashboard.html',
                         username=session.get('username'),
                         first_name=session.get('first_name'))

@app.route('/student/assignments')
@login_required
def student_assignments():
    """Student assignments page."""
    return render_template('student/assignments.html',
                         username=session.get('username'),
                         first_name=session.get('first_name'))

@app.route('/api/student/assignments')
@login_required
def get_student_assignments():
    """Get all assignments for the logged-in student."""
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.AssignmentID, a.ExamID, e.ExamName, e.TotalQuestions, 
                   a.DueDate, a.Status, 
                   COALESCE((SELECT Percentage FROM Results WHERE AssignmentID = a.AssignmentID AND StudentID = %s LIMIT 1), NULL) as Score
            FROM Assignments a
            JOIN Exams e ON a.ExamID = e.ExamID
            WHERE a.StudentID = %s
            ORDER BY a.DueDate DESC
        """, (user_id, user_id))
        
        assignments = cursor.fetchall()
        result = [
            {
                'assignmentID': row[0],
                'examID': row[1],
                'examName': row[2],
                'totalQuestions': row[3],
                'dueDate': row[4].strftime('%Y-%m-%d') if row[4] else '',
                'status': row[5],
                'score': float(row[6]) if row[6] else None
            }
            for row in assignments
        ]
        return jsonify({'assignments': result}), 200
    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/exams')
@login_required
def get_exams():
    """Get all exams for dropdown selection."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ExamID, ExamName FROM Exams ORDER BY ExamName ASC")
        exams = cursor.fetchall()
        result = [
            {
                'examID': row[0],
                'examName': row[1]
            }
            for row in exams
        ]
        return jsonify({'exams': result}), 200
    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/student/stats')
@login_required
def get_student_stats():
    """Get student statistics including total time spent on platform."""
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        
        # Get total time from ActivityLog
        cursor.execute("""
            SELECT SUM(Duration) as TotalSeconds
            FROM ActivityLog
            WHERE UserID = %s
        """, (user_id,))
        total_time_row = cursor.fetchone()
        total_seconds = total_time_row[0] if total_time_row[0] else 0
        total_hours = total_seconds / 3600
        
        # Get study hours (focus sessions only)
        cursor.execute("""
            SELECT SUM(Duration) as TotalSeconds
            FROM ActivityLog
            WHERE UserID = %s AND ActivityType = 'FocusSession'
        """, (user_id,))
        study_row = cursor.fetchone()
        study_seconds = study_row[0] if study_row[0] else 0
        study_hours = study_seconds / 3600
        
        # Get average score
        cursor.execute("""
            SELECT AVG(Percentage) FROM Results WHERE StudentID = %s
        """, (user_id,))
        avg_score_row = cursor.fetchone()
        avg_score = round(avg_score_row[0], 2) if avg_score_row[0] else 0
        
        # Get assignment stats
        cursor.execute("""
            SELECT COUNT(*) as Total, 
                   SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END) as Completed
            FROM Assignments
            WHERE StudentID = %s
        """, (user_id,))
        assignment_row = cursor.fetchone()
        total_assignments = assignment_row[0] if assignment_row[0] else 0
        completed_assignments = assignment_row[1] if assignment_row[1] else 0
        
        # Get achievements
        cursor.execute("""
            SELECT COUNT(*) FROM Achievements WHERE StudentID = %s
        """, (user_id,))
        achievements = cursor.fetchone()[0]
        
        return jsonify({
            'totalTime': round(total_hours, 2),
            'studyTime': round(study_hours, 2),
            'avgScore': avg_score,
            'totalAssignments': total_assignments,
            'completedAssignments': completed_assignments,
            'achievements': achievements
        }), 200
    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/teacher/doubts')
@login_required
@role_required('Teacher')
def teacher_doubts():
    """Return all doubts submitted by students in this teacher's classes."""
    teacher_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        # Get all doubts from students in teacher's classes
        cursor.execute("""
            SELECT d.DoubtID, d.StudentID, CONCAT(u.FirstName, ' ', u.LastName) as StudentName,
                   d.Topic, d.DoubtText, d.Status, d.ResolutionText, d.Timestamp, d.ImagePath
            FROM Doubts d
            JOIN Users u ON d.StudentID = u.UserID
            WHERE d.StudentID IN (
                SELECT DISTINCT StudentID FROM Assignments WHERE TeacherID = %s
            )
            ORDER BY 
                CASE WHEN d.Status = 'Pending' THEN 0
                     WHEN d.Status = 'In_Progress' THEN 1
                     WHEN d.Status = 'Cleared' THEN 2
                     ELSE 3 END,
                d.Timestamp DESC
        """, (teacher_id,))

        rows = cursor.fetchall()
        doubts = [
            {
                'doubtId': r[0],
                'studentId': r[1],
                'studentName': r[2],
                'topic': r[3],
                'doubtText': r[4],
                'status': r[5],
                'resolution': r[6],
                'createdAt': r[7].strftime('%Y-%m-%d %H:%M') if r[7] else '',
                'imagePath': r[8] or ''
            }
            for r in rows
        ]

        return jsonify({'doubts': doubts}), 200

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/teacher/respond-doubt', methods=['POST'])
@login_required
@role_required('Teacher')
def respond_doubt():
    """Teacher responds to a doubt: sets resolution text and marks resolved."""
    teacher_id = session.get('user_id')
    data = request.get_json()
    doubt_id = data.get('doubt_id')
    resolution = data.get('resolution')

    if not doubt_id or not resolution:
        return jsonify({'error': 'doubt_id and resolution are required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        # Ensure the doubt belongs to one of this teacher's students
        cursor.execute("""
            SELECT d.StudentID FROM Doubts d
            JOIN Assignments a ON d.StudentID = a.StudentID
            WHERE d.DoubtID = %s AND a.TeacherID = %s
        """, (doubt_id, teacher_id))

        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Doubt not found or not authorized'}), 404

        cursor.execute("""
            UPDATE Doubts
            SET TeacherID = %s, ResolutionText = %s, Status = 'Cleared', ResolvedAt = NOW()
            WHERE DoubtID = %s
        """, (teacher_id, resolution, doubt_id))

        conn.commit()
        return jsonify({'message': 'Doubt resolved successfully'}), 200

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/student/focus-session')
@login_required
def focus_sessions_page():
    """Focus sessions page - shows available exams for drilling."""
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return render_template('student/focus-session.html', exams=[], error='Database connection failed')

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ExamID, ExamName, TotalQuestions, TotalTime FROM Exams LIMIT 10")
        exams = cursor.fetchall()
        exam_list = [
            {'examID': e[0], 'examName': e[1], 'totalQuestions': e[2], 'totalTime': e[3]}
            for e in exams
        ]
        return render_template('student/focus-session.html',
                             exams=exam_list,
                             username=session.get('username'),
                             first_name=session.get('first_name'))
    except Error:
        return render_template('student/focus-session.html', exams=[], username=session.get('username'))
    finally:
        cursor.close()
        conn.close()

@app.route('/api/student/focus-session/<int:exam_id>')
@login_required
def get_focus_session_questions(exam_id):
    """Get questions for focus session drill with optional AI generation."""
    user_id = session.get('user_id')
    # AI integration removed — always use database-backed questions
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        # Get weak topics
        cursor.execute("""
            SELECT r.Topic FROM Results r
            WHERE r.StudentID = %s
            GROUP BY r.Topic
            ORDER BY AVG(r.Percentage) ASC LIMIT 2
        """, (user_id,))
        
        weak_topics = [row[0] for row in cursor.fetchall()]
        
        if weak_topics:
            placeholders = ','.join(['%s'] * len(weak_topics))
            query = f"""
                SELECT QuestionID, Topic, QuestionText, DifficultyLevel
                FROM Questions
                WHERE ExamID = %s AND Topic IN ({placeholders})
                ORDER BY RAND() LIMIT 10
            """
            cursor.execute(query, [exam_id] + weak_topics)
        else:
            cursor.execute("""
                SELECT QuestionID, Topic, QuestionText, DifficultyLevel
                FROM Questions
                WHERE ExamID = %s
                ORDER BY RAND() LIMIT 10
            """, (exam_id,))
        
        # Previously there was optional AI-generated questions here. AI support has been removed;
        # fall back to returning questions from the database only.
        
        questions = cursor.fetchall()
        result = [
            {
                'questionID': q[0],
                'topic': q[1],
                'text': q[2],
                'difficulty': q[3]
            }
            for q in questions
        ]
        return jsonify({'questions': result, 'aiGenerated': False}), 200
    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/student/focus-session/submit', methods=['POST'])
@login_required
def submit_focus_session():
    """Submit exam answers and save results."""
    user_id = session.get('user_id')
    data = request.get_json()
    print(f"[submit_focus_session] user={user_id} payload={data}")
    exam_id = data.get('examID')
    answers = data.get('answers', {})
    duration = data.get('duration', 0)
    score = data.get('score', 0)
    
    if not exam_id:
        return jsonify({'error': 'ExamID is required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Calculate correct answers
        correct_count = 0
        for qid, answer in answers.items():
            cursor.execute("""
                SELECT CorrectAnswer FROM Questions WHERE QuestionID = %s
            """, (int(qid),))
            result = cursor.fetchone()
            if result and result[0] == answer:
                correct_count += 1
        
        # Get total questions
        total_questions = len(answers) if answers else 0
        percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Insert result record
        cursor.execute("""
            INSERT INTO Results (StudentID, ExamID, Percentage, TimeSpent, AnswersCorrect)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, exam_id, percentage, duration, correct_count))
        
        conn.commit()
        
        # Check and award achievements
        check_and_award_achievements(user_id)
        
        return jsonify({
            'success': True,
            'percentage': percentage,
            'correctAnswers': correct_count,
            'totalQuestions': total_questions
        }), 200
        
    except Error as err:
        conn.rollback()
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/student/doubts')
@login_required
def student_doubts():
    """Student doubts page."""
    return render_template('student/doubts.html',
                         username=session.get('username'),
                         first_name=session.get('first_name'))

@app.route('/api/student/doubts')
@login_required
def get_student_doubts():
    """Get all doubts submitted by the student."""
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.DoubtID, d.Topic, d.DoubtText, d.Status, d.ResolutionText, 
                   d.Timestamp, CONCAT(u.FirstName, ' ', u.LastName) as TeacherName, d.ImagePath
            FROM Doubts d
            LEFT JOIN Users u ON d.TeacherID = u.UserID
            WHERE d.StudentID = %s
            ORDER BY d.Timestamp DESC
        """, (user_id,))
        
        doubts = cursor.fetchall()
        result = [
            {
                'doubtID': row[0],
                'topic': row[1],
                'text': row[2],
                'status': row[3],
                'resolution': row[4],
                'createdAt': row[5].strftime('%Y-%m-%d %H:%M') if row[5] else '',
                'teacherName': row[6] or 'Pending',
                'imagePath': row[7]
            }
            for row in doubts
        ]
        return jsonify({'doubts': result}), 200
    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/student/achievements')
@login_required
def student_achievements():
    """Student achievements page."""
    return render_template('student/achievements.html',
                         username=session.get('username'),
                         first_name=session.get('first_name'))

@app.route('/api/student/achievements')
@login_required
def get_student_achievements():
    """Get all achievements for the student."""
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT AchievementID, TrophyName, Description, Badge, Points, DateEarned
            FROM Achievements
            WHERE StudentID = %s
            ORDER BY DateEarned DESC
        """, (user_id,))
        
        achievements = cursor.fetchall()
        result = [
            {
                'achievementID': row[0],
                'trophyName': row[1],
                'description': row[2],
                'badge': row[3],
                'points': row[4],
                'dateEarned': row[5].strftime('%Y-%m-%d') if row[5] else ''
            }
            for row in achievements
        ]
        return jsonify({'achievements': result, 'totalPoints': sum([a['points'] for a in result])}), 200
    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/student/analytics')
@login_required
def student_analytics():
    """Student analytics page."""
    return render_template('student/analytics.html',
                         username=session.get('username'),
                         first_name=session.get('first_name'))

@app.route('/api/student/analytics')
@login_required
def get_student_analytics():
    """Get comprehensive analytics for the student."""
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute("""
            SELECT COUNT(DISTINCT ResultID) as TotalTests,
                   AVG(Percentage) as AvgScore,
                   MAX(Percentage) as BestScore,
                   MIN(Percentage) as LowestScore
            FROM Results
            WHERE StudentID = %s
        """, (user_id,))
        
        stats = cursor.fetchone()
        
        # Topic-wise performance
        cursor.execute("""
            SELECT Topic, COUNT(*) as AttemptCount, AVG(Percentage) as AvgScore, MAX(Percentage) as BestScore
            FROM Results
            WHERE StudentID = %s
            GROUP BY Topic
            ORDER BY AvgScore DESC
        """, (user_id,))
        
        topics = cursor.fetchall()
        
        # Time stats
        cursor.execute("""
            SELECT ActivityType, COUNT(*) as Count, SUM(Duration) as TotalSeconds
            FROM ActivityLog
            WHERE UserID = %s
            GROUP BY ActivityType
        """, (user_id,))
        
        activities = cursor.fetchall()
        
        return jsonify({
            'overallStats': {
                'totalTests': stats[0] or 0,
                'avgScore': float(stats[1]) if stats[1] else 0,
                'bestScore': float(stats[2]) if stats[2] else 0,
                'lowestScore': float(stats[3]) if stats[3] else 0
            },
            'topicPerformance': [
                {
                    'topic': t[0],
                    'attemptCount': t[1],
                    'avgScore': float(t[2]),
                    'bestScore': float(t[3])
                }
                for t in topics
            ],
            'activityStats': [
                {
                    'activityType': a[0],
                    'count': a[1],
                    'totalHours': round(a[2] / 3600, 2) if a[2] else 0
                }
                for a in activities
            ]
        }), 200
    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/student/weakness-topics')
@login_required
def get_weakness_topics():
    """
    Identify student's weakest topics based on test results.
    Returns the two topics with lowest average scores.
    """
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        
        # Query: Get average score by topic for the student
        cursor.execute("""
            SELECT r.Topic, AVG(r.Percentage) as AvgPercentage, COUNT(r.ResultID) as AttemptCount
            FROM Results r
            WHERE r.StudentID = %s
            GROUP BY r.Topic
            ORDER BY AvgPercentage ASC
            LIMIT 2
        """, (user_id,))

        weakness_topics = cursor.fetchall()
        
        if not weakness_topics:
            return jsonify({'weaknessTopics': [], 'message': 'No test data available yet'}), 200

        result = [
            {
                'topic': row[0],
                'avgPercentage': float(row[1]),
                'attemptCount': int(row[2])
            }
            for row in weakness_topics
        ]

        return jsonify({'weaknessTopics': result}), 200

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/student/focus-session/<int:exam_id>')
@login_required
def focus_session(exam_id):
    """
    Fetch 10 random questions from the student's two weakest topics
    for targeted drilling.
    """
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        
        # Get two weakest topics
        cursor.execute("""
            SELECT r.Topic FROM Results r
            WHERE r.StudentID = %s
            GROUP BY r.Topic
            ORDER BY AVG(r.Percentage) ASC
            LIMIT 2
        """, (user_id,))
        
        topics = [row[0] for row in cursor.fetchall()]
        
        if not topics:
            return jsonify({'error': 'No weakness data available'}), 400

        # Fetch 10 random questions from weakest topics
        placeholders = ','.join(['%s'] * len(topics))
        cursor.execute(f"""
            SELECT QuestionID, QuestionText, Options, Topic, SubTopic
            FROM Questions
            WHERE ExamID = %s AND Topic IN ({placeholders})
            ORDER BY RAND()
            LIMIT 10
        """, [exam_id] + topics)

        questions = cursor.fetchall()
        
        result = [
            {
                'questionId': row[0],
                'questionText': row[1],
                'options': json.loads(row[2]),
                'topic': row[3],
                'subTopic': row[4]
            }
            for row in questions
        ]

        return jsonify({
            'focusTopics': topics,
            'questions': result,
            'totalQuestions': len(result)
        }), 200

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/log-activity', methods=['POST'])
@login_required
def log_activity():
    """
    Log user activity (focus sessions, login, test start/submit).
    Expects: activity_type, duration (optional), exam_id (optional), assignment_id (optional)
    """
    user_id = session.get('user_id')
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    activity_type = data.get('activity_type')
    duration = data.get('duration')  # in seconds
    exam_id = data.get('exam_id')
    assignment_id = data.get('assignment_id')
    details = data.get('details', {})

    if not activity_type:
        return jsonify({'error': 'activity_type is required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ActivityLog (UserID, ActivityType, Duration, ExamID, AssignmentID, Details)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, activity_type, duration, exam_id, assignment_id, json.dumps(details)))
        
        conn.commit()
        
        # Check if achievements can be awarded
        check_and_award_achievements(user_id)
        
        return jsonify({'message': 'Activity logged successfully'}), 201

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/student/submit-doubt', methods=['POST'])
@login_required
def submit_doubt():
    """
    Submit a doubt/question for teacher resolution.
    Can include QuestionID from past papers or free-form topic.
    Can also include image attachments.
    """
    user_id = session.get('user_id')
    topic = request.form.get('topic', '').strip()
    doubt_text = request.form.get('doubt_text', '').strip()
    question_id = request.form.get('question_id')
    priority = request.form.get('priority', 'Medium')
    
    image_path = None
    
    if not topic or not doubt_text:
        return jsonify({'error': 'Topic and doubt description are required'}), 400

    # Handle image upload if provided
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            # Validate file type
            allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
            if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                try:
                    # Create uploads/doubts directory if it doesn't exist
                    upload_dir = os.path.join('uploads', 'doubts')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Save file with timestamp to avoid conflicts
                    filename = secure_filename(f"{int(time.time())}_{file.filename}")
                    filepath = os.path.join(upload_dir, filename)
                    file.save(filepath)
                    image_path = f"uploads/doubts/{filename}"
                except Exception as e:
                    print(f"File upload error: {e}")
                    return jsonify({'error': f'File upload failed: {str(e)}'}), 500

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        # Validate priority value
        if priority not in ['Low', 'Medium', 'High']:
            priority = 'Medium'
        
        cursor.execute("""
            INSERT INTO Doubts (StudentID, Topic, DoubtText, QuestionID, Priority, Status, ImagePath)
            VALUES (%s, %s, %s, %s, %s, 'Pending', %s)
        """, (user_id, topic, doubt_text, question_id if question_id else None, priority, image_path))
        
        conn.commit()
        
        return jsonify({
            'message': 'Doubt submitted successfully',
            'doubtId': cursor.lastrowid
        }), 201

    except Error as err:
        conn.rollback()
        print(f"Database error in submit_doubt: {err}")
        return jsonify({'error': f'Failed to submit doubt: {str(err)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/student/performance')
@login_required
def student_performance():
    """
    Fetch student performance metrics for chart visualization.
    Returns: progression over time, breakdown by topic/subtopic.
    """
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        
        # Progression over time (last 10 results)
        cursor.execute("""
            SELECT DATE(Timestamp) as DateOnly, AVG(Percentage) as AvgPercentage
            FROM Results
            WHERE StudentID = %s
            GROUP BY DATE(Timestamp)
            ORDER BY DateOnly DESC
            LIMIT 10
        """, (user_id,))
        
        progression = [{'date': str(row[0]), 'percentage': float(row[1])} for row in cursor.fetchall()]
        
        # Topic breakdown
        cursor.execute("""
            SELECT Topic, AVG(Percentage) as AvgPercentage, COUNT(*) as TestCount
            FROM Results
            WHERE StudentID = %s
            GROUP BY Topic
        """, (user_id,))
        
        topic_breakdown = [
            {'topic': row[0], 'percentage': float(row[1]), 'testCount': int(row[2])}
            for row in cursor.fetchall()
        ]
        
        # Study hours this week
        cursor.execute("""
            SELECT SUM(Duration) as TotalSeconds
            FROM ActivityLog
            WHERE UserID = %s AND ActivityType = 'FocusSession'
            AND Timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """, (user_id,))
        
        study_hours_row = cursor.fetchone()
        study_hours = (study_hours_row[0] / 3600) if study_hours_row[0] else 0
        
        return jsonify({
            'progression': progression,
            'topicBreakdown': topic_breakdown,
            'studyHoursThisWeek': float(study_hours)
        }), 200

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/student/class-stats')
@login_required
def student_class_stats():
    """Get class-wide statistics for display on student dashboard."""
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        
        # Find the teacher assigned to this student
        cursor.execute("""
            SELECT DISTINCT a.TeacherID
            FROM Assignments a
            WHERE a.StudentID = %s
            LIMIT 1
        """, (user_id,))
        teacher_row = cursor.fetchone()
        if not teacher_row:
            # No teacher assigned, return default stats
            return jsonify({
                'totalStudents': 0,
                'totalAssignments': 0,
                'completedAssignments': 0,
                'totalExams': 0,
                'totalTestsTaken': 0,
                'averagePerformance': 0.0,
                'pendingDoubts': 0
            }), 200
        
        teacher_id = teacher_row[0]
        
        # Total students
        cursor.execute("""
            SELECT COUNT(DISTINCT StudentID)
            FROM Assignments
            WHERE TeacherID = %s
        """, (teacher_id,))
        total_students = cursor.fetchone()[0] or 0
        
        # Total assignments given
        cursor.execute("""
            SELECT COUNT(*) FROM Assignments WHERE TeacherID = %s
        """, (teacher_id,))
        total_assignments = cursor.fetchone()[0] or 0
        
        # Completed assignments
        cursor.execute("""
            SELECT COUNT(*) FROM Assignments WHERE TeacherID = %s AND Status = 'Completed'
        """, (teacher_id,))
        completed_assignments = cursor.fetchone()[0] or 0
        
        # Total tests available (count all exams)
        cursor.execute("""
            SELECT COUNT(DISTINCT ExamID) FROM Exams
        """)
        total_exams = cursor.fetchone()[0] or 0
        
        # Total test attempts from assigned students
        cursor.execute("""
            SELECT COUNT(*)
            FROM Results r
            JOIN Assignments a ON r.StudentID = a.StudentID
            WHERE a.TeacherID = %s
        """, (teacher_id,))
        total_tests_taken = cursor.fetchone()[0] or 0
        
        # Average student performance
        cursor.execute("""
            SELECT AVG(r.Percentage)
            FROM Results r
            JOIN Assignments a ON r.StudentID = a.StudentID
            WHERE a.TeacherID = %s
        """, (teacher_id,))
        avg_performance = cursor.fetchone()[0] or 0
        
        # Pending doubts
        cursor.execute("""
            SELECT COUNT(*)
            FROM Doubts d
            WHERE d.TeacherID = %s AND d.Status = 'Pending'
        """, (teacher_id,))
        pending_doubts = cursor.fetchone()[0] or 0
        
        return jsonify({
            'totalStudents': total_students,
            'totalAssignments': total_assignments,
            'completedAssignments': completed_assignments,
            'totalExams': total_exams,
            'totalTestsTaken': total_tests_taken,
            'averagePerformance': round(float(avg_performance), 2),
            'pendingDoubts': pending_doubts
        }), 200

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================================
# HTMX / Partial endpoints
# ============================================================================
@app.route('/_htmx/recent-activity')
@login_required
def htmx_recent_activity():
    """Return a small partial showing recent activity for the logged-in user.
    This is intended for HTMX-driven partial updates and the floating widget.
    """
    user_id = session.get('user_id')
    activities = []
    conn = get_db_connection()
    if not conn:
        return render_template('partials/recent_activity.html', activities=[])

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ActivityType, Duration, ExamID, AssignmentID, Details, Timestamp
            FROM ActivityLog
            WHERE UserID = %s
            ORDER BY Timestamp DESC
            LIMIT 5
        """, (user_id,))
        rows = cursor.fetchall()
        # Map rows to simple objects for template consumption
        for r in rows:
            activities.append({
                'ActivityType': r[0],
                'Duration': r[1],
                'ExamID': r[2],
                'AssignmentID': r[3],
                'Details': json.loads(r[4]) if r[4] else {},
                'Timestamp': r[5]
            })
    except Exception:
        activities = []
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

    return render_template('partials/recent_activity.html', activities=activities)


@app.route('/_htmx/focus-session/<int:exam_id>')
@login_required
def htmx_focus_session(exam_id):
    """Return an HTMX partial rendering the focus session Alpine component."""
    print(f"[htmx_focus_session] requested exam_id={exam_id}")
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        # render empty partial with metadata and empty questions array
        rendered = render_template('partials/focus_session_inner.html', exam_id=exam_id, exam_name=f'Exam {exam_id}', questions=[])
        wrapper = f"""
<div data-exam-id="{exam_id}" data-exam-name="Exam {exam_id}">
    <script type=\"application/json\">{json.dumps([])}</script>
    {rendered}
</div>
"""
        return wrapper

    try:
        cursor = conn.cursor()
        # Get exam name
        cursor.execute("SELECT ExamName FROM Exams WHERE ExamID = %s", (exam_id,))
        row = cursor.fetchone()
        exam_name = row[0] if row else f'Exam {exam_id}'

        # Fetch questions from DB
        cursor.execute("""
            SELECT QuestionID, Topic, QuestionText, DifficultyLevel, Options
            FROM Questions
            WHERE ExamID = %s
            ORDER BY RAND()
            LIMIT 10
        """, (exam_id,))
        rows = cursor.fetchall()
        questions = []
        for r in rows:
            options = []
            try:
                options = json.loads(r[4]) if r[4] else []
            except Exception:
                options = []
            questions.append({
                'questionID': r[0],
                'topic': r[1],
                'text': r[2],
                'difficulty': r[3] or 'Medium',
                'options': options
            })
    except Exception:
        questions = []
        exam_name = f'Exam {exam_id}'
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

    # If no questions found for this exam, try a fallback random pool (outside finally)
    fallback_used = False
    if not questions:
        print(f"[htmx_focus_session] no questions found for exam {exam_id}; trying fallback pool")
        try:
            conn2 = get_db_connection()
            if conn2:
                cur2 = conn2.cursor()
                cur2.execute("""
                    SELECT QuestionID, Topic, QuestionText, DifficultyLevel, Options
                    FROM Questions
                    ORDER BY RAND()
                    LIMIT 10
                """)
                rows = cur2.fetchall()
                for r in rows:
                    options = []
                    try:
                        options = json.loads(r[4]) if r[4] else []
                    except Exception:
                        options = []
                    questions.append({
                        'questionID': r[0],
                        'topic': r[1],
                        'text': r[2],
                        'difficulty': r[3] or 'Medium',
                        'options': options
                    })
                try:
                    cur2.close()
                except Exception:
                    pass
                try:
                    conn2.close()
                except Exception:
                    pass
                if questions:
                    fallback_used = True
        except Exception as e:
            print(f"[htmx_focus_session] fallback query failed: {e}")

    # Render partial and always return a wrapper embedding the questions JSON so the
    # Alpine/HTMX client can reliably find its data.
    rendered = render_template('partials/focus_session_inner.html', exam_id=exam_id, exam_name=exam_name, questions=questions)
    print(f"[htmx_focus_session] returning {len(questions)} questions for exam {exam_id} (fallback={fallback_used})")

    wrapper = f"""
<div data-exam-id="{exam_id}" data-exam-name="{exam_name}" data-fallback="{json.dumps(fallback_used)}">
    <script type=\"application/json\">{json.dumps(questions)}</script>
    {rendered}
</div>
"""
    return wrapper

# ============================================================================
# TEACHER PORTAL ROUTES
# ============================================================================
@app.route('/teacher/dashboard')
@login_required
@role_required('Teacher')
def teacher_dashboard():
    """Teacher dashboard with student management and analytics."""
    return render_template('teacher/dashboard.html',
                         username=session.get('username'),
                         first_name=session.get('first_name'))

@app.route('/teacher/student-performance')
@login_required
@role_required('Teacher')
def student_performance_page():
    """Page showing all students with their performance metrics."""
    return render_template('teacher/student-performance.html',
                         username=session.get('username'),
                         first_name=session.get('first_name'))

@app.route('/api/teacher/student-roster')
@login_required
@role_required('Teacher')
def student_roster():
    """
    Fetch all assigned students with their engagement scores.
    Engagement Score = (Study Hours * 0.3) + (Completion Rate * 0.4) + (Trophy Count * 0.3)
    """
    teacher_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        
        # Get all unique students assigned to this teacher
        cursor.execute("""
            SELECT DISTINCT a.StudentID, u.FirstName, u.LastName, u.Username
            FROM Assignments a
            JOIN Users u ON a.StudentID = u.UserID
            WHERE a.TeacherID = %s
        """, (teacher_id,))
        
        students = cursor.fetchall()
        # If teacher has very few assigned students, fall back to returning all students
        # so the teacher can view wider roster (useful in small test data setups).
        assigned_mode = True
        if not students or len(students) < 5:
            cursor.execute("""
                SELECT UserID, FirstName, LastName, Username
                FROM Users
                WHERE Role = 'Student'
                ORDER BY FirstName, LastName
            """)
            students = cursor.fetchall()
            assigned_mode = False
        roster = []
        
        for student in students:
            student_id, first_name, last_name, username = student
            
            # Calculate study hours (last 30 days)
            cursor.execute("""
                SELECT SUM(Duration) as TotalSeconds
                FROM ActivityLog
                WHERE UserID = %s AND ActivityType = 'FocusSession'
                AND Timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """, (student_id,))
            study_hours_row = cursor.fetchone()
            study_hours = float((study_hours_row[0] / 3600) if study_hours_row[0] else 0)
            
            # Calculate completion rate
            if assigned_mode:
                cursor.execute("""
                    SELECT COUNT(CASE WHEN Status = 'Completed' THEN 1 END) as Completed,
                           COUNT(*) as Total
                    FROM Assignments
                    WHERE StudentID = %s AND TeacherID = %s
                """, (student_id, teacher_id))
            else:
                # When listing all students (fallback), compute completion regardless of teacher
                cursor.execute("""
                    SELECT COUNT(CASE WHEN Status = 'Completed' THEN 1 END) as Completed,
                           COUNT(*) as Total
                    FROM Assignments
                    WHERE StudentID = %s
                """, (student_id,))
            completion_row = cursor.fetchone()
            # Apply Bayesian smoothing to avoid extreme 0%/100% values for small sample sizes.
            # Use a weak prior: prior_mean = 0.40 (40%), prior_weight = 2 pseudo-observations.
            completed = int(completion_row[0] or 0)
            total = int(completion_row[1] or 0)
            prior_mean = 0.40
            prior_weight = 2
            if (total + prior_weight) > 0:
                completion_rate = float((completed + prior_mean * prior_weight) / (total + prior_weight) * 100)
            else:
                completion_rate = 0.0
            
            # Count trophies
            cursor.execute("""
                SELECT COUNT(*) FROM Achievements WHERE StudentID = %s
            """, (student_id,))
            trophy_count = cursor.fetchone()[0]
            
            # Calculate engagement score
            engagement_score = (study_hours * 0.3) + (completion_rate * 0.004) + (trophy_count * 10)
            
            roster.append({
                'studentId': student_id,
                'name': f"{first_name} {last_name}",
                'username': username,
                'engagementScore': round(engagement_score, 2),
                'studyHours': round(study_hours, 1),
                'completionRate': round(completion_rate, 1),
                'trophyCount': trophy_count,
                'scoreLevel': 'High' if engagement_score >= 70 else 'Medium' if engagement_score >= 40 else 'Low'
            })
        
        # Sort by engagement score descending
        roster.sort(key=lambda x: x['engagementScore'], reverse=True)
        
        return jsonify({'students': roster}), 200

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/teacher/stats')
@login_required
@role_required('Teacher')
def get_teacher_stats():
    """Get teacher dashboard statistics including total student study hours."""
    teacher_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        
        # Get assigned students
        cursor.execute("""
            SELECT COUNT(DISTINCT StudentID)
            FROM Assignments
            WHERE TeacherID = %s
        """, (teacher_id,))
        total_students = cursor.fetchone()[0] or 0
        
        # Get total study hours from all assigned students
        cursor.execute("""
            SELECT SUM(al.Duration) as TotalSeconds
            FROM ActivityLog al
            JOIN Assignments a ON al.UserID = a.StudentID
            WHERE a.TeacherID = %s AND al.ActivityType = 'FocusSession'
        """, (teacher_id,))
        study_hours_row = cursor.fetchone()
        total_study_hours = float((study_hours_row[0] / 3600) if study_hours_row[0] else 0)
        
        # Get average completion rate
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN Status = 'Completed' THEN 1 END) as Completed,
                COUNT(*) as Total
            FROM Assignments
            WHERE TeacherID = %s
        """, (teacher_id,))
        completion_row = cursor.fetchone()
        # Bayesian smoothing for aggregated completion rate as well
        completed = int(completion_row[0] or 0)
        total = int(completion_row[1] or 0)
        prior_mean = 0.40
        prior_weight = 2
        if (total + prior_weight) > 0:
            completion_rate = float((completed + prior_mean * prior_weight) / (total + prior_weight) * 100)
        else:
            completion_rate = 0.0
        
        # Get pending doubts
        cursor.execute("""
            SELECT COUNT(*) FROM Doubts
            WHERE TeacherID = %s AND Status = 'Pending'
        """, (teacher_id,))
        pending_doubts = cursor.fetchone()[0] or 0
        
        return jsonify({
            'totalStudents': total_students,
            'totalStudyHours': round(total_study_hours, 2),
            'completionRate': round(completion_rate, 1),
            'pendingDoubts': pending_doubts
        }), 200
    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/teacher/all-students')
@login_required
@role_required('Teacher')
def get_all_students_performance():
    """Fetch all students with their performance metrics (not just assigned students)."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        
        # Get all students in the system
        cursor.execute("""
            SELECT UserID, FirstName, LastName, Username, CreatedAt
            FROM Users
            WHERE Role = 'Student'
            ORDER BY FirstName, LastName
        """)
        
        students = cursor.fetchall()
        roster = []
        
        for student in students:
            try:
                student_id, first_name, last_name, username, created_at = student
                
                # Calculate study hours (total from ActivityLog)
                cursor.execute("""
                    SELECT SUM(Duration) as TotalSeconds
                    FROM ActivityLog
                    WHERE UserID = %s AND ActivityType = 'FocusSession'
                """, (student_id,))
                study_hours_row = cursor.fetchone()
                study_hours = float((study_hours_row[0] / 3600) if study_hours_row[0] else 0)
                
                # Calculate total time using all activities
                cursor.execute("""
                    SELECT SUM(Duration) as TotalSeconds
                    FROM ActivityLog
                    WHERE UserID = %s
                """, (student_id,))
                total_time_row = cursor.fetchone()
                total_time = float((total_time_row[0] / 3600) if total_time_row[0] else 0)
                
                # Get average test score
                cursor.execute("""
                    SELECT AVG(Percentage) FROM Results WHERE StudentID = %s
                """, (student_id,))
                avg_score_row = cursor.fetchone()
                avg_score = float(round(avg_score_row[0], 2) if avg_score_row[0] else 0)
                
                # Count assignments completed
                cursor.execute("""
                    SELECT COUNT(*) FROM Assignments WHERE StudentID = %s AND Status = 'Completed'
                """, (student_id,))
                completed_assignments = int(cursor.fetchone()[0] or 0)
                
                # Count achievements
                cursor.execute("""
                    SELECT COUNT(*) FROM Achievements WHERE StudentID = %s
                """, (student_id,))
                achievements = int(cursor.fetchone()[0] or 0)
                
                roster.append({
                    'studentId': student_id,
                    'name': f"{first_name or ''} {last_name or ''}".strip() or 'Unknown',
                    'username': username or 'unknown',
                    'studyHours': round(study_hours, 2),
                    'totalTime': round(total_time, 2),
                    'avgScore': avg_score,
                    'completedAssignments': completed_assignments,
                    'achievements': achievements,
                    'joinDate': created_at.strftime('%Y-%m-%d') if created_at else '',
                    'performanceLevel': 'High' if avg_score >= 80 else 'Good' if avg_score >= 70 else 'Average' if avg_score >= 60 else 'Below Average'
                })
            except Exception as e:
                # Log error but continue processing other students
                print(f"Error processing student {student_id if 'student_id' in locals() else 'unknown'}: {e}")
                continue
        
        # Sort by average score descending
        roster.sort(key=lambda x: x['avgScore'], reverse=True)
        
        return jsonify({'students': roster}), 200

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/teachers')
@login_required
@role_required('Teacher')
def admin_teachers():
    """Return list of teachers with aggregated metrics for the roster page."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT UserID, FirstName, LastName, Username, CreatedAt
            FROM Users
            WHERE Role = 'Teacher'
            ORDER BY FirstName, LastName
        """)
        teachers = cursor.fetchall()
        result = []
        for t in teachers:
            teacher_id, first_name, last_name, username, created_at = t

            # Total students assigned
            cursor.execute("""
                SELECT COUNT(DISTINCT StudentID) FROM Assignments WHERE TeacherID = %s
            """, (teacher_id,))
            total_students = cursor.fetchone()[0] or 0

            # Average student score for this teacher
            cursor.execute("""
                SELECT AVG(r.Percentage) FROM Results r
                JOIN Assignments a ON r.StudentID = a.StudentID
                WHERE a.TeacherID = %s
            """, (teacher_id,))
            avg_score = cursor.fetchone()[0] or 0
            avg_score = round(float(avg_score), 2)

            # Total assignments
            cursor.execute("""
                SELECT COUNT(*) FROM Assignments WHERE TeacherID = %s
            """, (teacher_id,))
            total_assignments = cursor.fetchone()[0] or 0

            # Doubts resolved and pending
            cursor.execute("""
                SELECT COUNT(*) FROM Doubts WHERE TeacherID = %s AND Status = 'Cleared'
            """, (teacher_id,))
            doubts_resolved = cursor.fetchone()[0] or 0
            cursor.execute("""
                SELECT COUNT(*) FROM Doubts WHERE TeacherID = %s AND Status = 'Pending'
            """, (teacher_id,))
            doubts_pending = cursor.fetchone()[0] or 0

            result.append({
                'teacherId': teacher_id,
                'name': f"{first_name} {last_name}",
                'username': username,
                'joinDate': created_at.strftime('%Y-%m-%d') if created_at else '',
                'totalStudents': total_students,
                'avgStudentScore': avg_score,
                'totalAssignments': total_assignments,
                'doubtsResolved': doubts_resolved,
                'pendingDoubts': doubts_pending,
                'performanceRating': 'Excellent' if avg_score >= 85 else 'Good' if avg_score >= 70 else 'Average'
            })

        return jsonify({'teachers': result}), 200
    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/teacher/assignment/create', methods=['POST'])
@login_required
@role_required('Teacher')
def create_assignment():
    """Create a new assignment for a student or group."""
    teacher_id = session.get('user_id')
    data = request.get_json()
    exam_id = data.get('exam_id')
    student_ids = data.get('student_ids', [])
    due_date = data.get('due_date')

    if not exam_id or not student_ids:
        return jsonify({'error': 'exam_id and student_ids are required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        assignment_ids = []
        
        for student_id in student_ids:
            # Check if assignment already exists
            cursor.execute("""
                SELECT AssignmentID FROM Assignments
                WHERE TeacherID = %s AND StudentID = %s AND ExamID = %s
            """, (teacher_id, student_id, exam_id))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO Assignments (TeacherID, StudentID, ExamID, Status, DueDate)
                    VALUES (%s, %s, %s, 'Assigned', %s)
                """, (teacher_id, student_id, exam_id, due_date))
                assignment_ids.append(cursor.lastrowid)
        
        conn.commit()
        
        return jsonify({
            'message': 'Assignments created successfully',
            'assignmentIds': assignment_ids
        }), 201

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/teacher/assignment/create-simple', methods=['POST'])
@login_required
@role_required('Teacher')
def create_simple_assignment():
    """Create a simple assignment by assigning an exam to students with a due date."""
    teacher_id = session.get('user_id')
    exam_id = request.form.get('exam_id')
    due_date = request.form.get('due_date')

    if not exam_id or not due_date:
        return jsonify({'error': 'exam_id and due_date are required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        
        # Get all students this teacher has taught
        cursor.execute("""
            SELECT DISTINCT StudentID FROM Assignments WHERE TeacherID = %s
        """, (teacher_id,))
        
        student_ids = [row[0] for row in cursor.fetchall()]
        
        if not student_ids:
            # If no students yet, get all active students
            cursor.execute("SELECT UserID FROM Users WHERE Role = 'Student' AND IsActive = 1")
            student_ids = [row[0] for row in cursor.fetchall()]
        
        created_count = 0
        for student_id in student_ids:
            # Check if assignment already exists
            cursor.execute("""
                SELECT AssignmentID FROM Assignments 
                WHERE StudentID = %s AND TeacherID = %s AND ExamID = %s
            """, (student_id, teacher_id, exam_id))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO Assignments (StudentID, TeacherID, ExamID, DueDate, Status)
                    VALUES (%s, %s, %s, %s, 'Assigned')
                """, (student_id, teacher_id, exam_id, due_date))
                created_count += 1
        
        conn.commit()
        
        return jsonify({
            'message': f'Assignment created and assigned to {created_count} students',
            'studentCount': created_count
        }), 201

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/teacher/analysis/question-effectiveness', methods=['POST'])
@login_required
@role_required('Teacher')
def question_effectiveness():
    """
    Analyze question effectiveness: average completion time and success rate.
    Expects: exam_id
    """
    teacher_id = session.get('user_id')
    data = request.get_json()
    exam_id = data.get('exam_id')

    if not exam_id:
        return jsonify({'error': 'exam_id is required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        
        # Verify teacher owns this exam
        cursor.execute("""
            SELECT DISTINCT q.TeacherID FROM Questions q WHERE q.ExamID = %s
        """, (exam_id,))
        
        # Get all questions and their performance metrics
        cursor.execute("""
            SELECT q.QuestionID, q.QuestionText, q.Topic, q.SubTopic,
                   AVG(r.CompletionTime) as AvgCompletionTime,
                   COUNT(r.ResultID) as TotalAttempts,
                   SUM(CASE WHEN r.Percentage >= 50 THEN 1 ELSE 0 END) as SuccessCount
            FROM Questions q
            LEFT JOIN Results r ON r.Topic = q.Topic AND r.StudentID IN (
                SELECT StudentID FROM Assignments WHERE TeacherID = %s AND ExamID = %s
            )
            WHERE q.ExamID = %s
            GROUP BY q.QuestionID, q.QuestionText, q.Topic, q.SubTopic
            ORDER BY (SUM(CASE WHEN r.Percentage >= 50 THEN 1 ELSE 0 END) / COUNT(r.ResultID)) ASC
        """, (teacher_id, exam_id, exam_id))

        analysis = []
        for row in cursor.fetchall():
            question_id, question_text, topic, subtopic, avg_time, attempts, success_count = row
            success_rate = (success_count / attempts * 100) if attempts > 0 else 0
            
            analysis.append({
                'questionId': question_id,
                'questionText': question_text[:100] + '...' if len(question_text) > 100 else question_text,
                'topic': topic,
                'subTopic': subtopic,
                'avgCompletionTime': float(avg_time) if avg_time else 0,
                'totalAttempts': int(attempts) if attempts else 0,
                'successRate': round(success_rate, 2),
                'difficulty': 'High' if success_rate < 30 else 'Medium' if success_rate < 70 else 'Low'
            })
        
        return jsonify({'analysis': analysis}), 200

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/teacher/doubts-frequency')
@login_required
@role_required('Teacher')
def doubts_frequency():
    """Get frequency of doubts by topic for the teacher's students."""
    teacher_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT d.Topic, COUNT(d.DoubtID) as DoubtCount
            FROM Doubts d
            JOIN Assignments a ON d.StudentID = a.StudentID
            WHERE a.TeacherID = %s
            GROUP BY d.Topic
            ORDER BY DoubtCount DESC
        """, (teacher_id,))

        doubts = [{'topic': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        return jsonify({'doubtsByTopic': doubts}), 200

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# GAMIFICATION & ACHIEVEMENT LOGIC
# ============================================================================
def check_and_award_achievements(user_id):
    """
    Check and award achievements based on student performance and activity.
    Achievements:
    - "Focused Learner": 5+ hours of study in a week
    - "Consistent": 7 consecutive days of login
    - "High Scorer": 90%+ in any test
    - "Problem Solver": Cleared 5+ doubts
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        # Check "Focused Learner" (5+ hours this week)
        cursor.execute("""
            SELECT SUM(Duration) FROM ActivityLog
            WHERE UserID = %s AND ActivityType = 'FocusSession'
            AND Timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """, (user_id,))
        
        study_seconds = cursor.fetchone()[0] or 0
        if study_seconds >= 18000:  # 5 hours = 18000 seconds
            cursor.execute("""
                SELECT AchievementID FROM Achievements
                WHERE StudentID = %s AND TrophyName = 'Focused Learner'
            """, (user_id,))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO Achievements (StudentID, TrophyName, Description, Badge, Points)
                    VALUES (%s, 'Focused Learner', 'Completed 5+ hours of focused study sessions', 'focus-badge', 50)
                """, (user_id,))
                conn.commit()
        
        # Check "High Scorer" (90%+ in any test)
        cursor.execute("""
            SELECT COUNT(*) FROM Achievements
            WHERE StudentID = %s AND TrophyName = 'High Scorer'
        """, (user_id,))
        
        existing = cursor.fetchone()[0]
        if existing == 0:
            cursor.execute("""
                SELECT COUNT(DISTINCT ResultID) FROM Results
                WHERE StudentID = %s AND Percentage >= 90
            """, (user_id,))
            
            high_scores = cursor.fetchone()[0]
            if high_scores > 0:
                cursor.execute("""
                    INSERT INTO Achievements (StudentID, TrophyName, Description, Badge, Points)
                    VALUES (%s, 'High Scorer', 'Scored 90% or higher on a test', 'star-badge', 100)
                """, (user_id,))
                conn.commit()

    except Error:
        pass
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEACHER PORTAL - ADDITIONAL PAGES
# ============================================================================

@app.route('/teacher/students')
@login_required
@role_required('Teacher')
def teacher_students():
    """Teacher Student Roster page."""
    return render_template('teacher/students.html',
                         username=session.get('username'),
                         first_name=session.get('first_name'))

@app.route('/teacher/assignments')
@login_required
@role_required('Teacher')
def teacher_assignments():
    """Teacher Assignments management page."""
    return render_template('teacher/assignments.html',
                         username=session.get('username'),
                         first_name=session.get('first_name'))

@app.route('/teacher/analytics')
@login_required
@role_required('Teacher')
def teacher_analytics():
    """Teacher Analytics page with class-wide metrics."""
    return render_template('teacher/analytics.html',
                         username=session.get('username'),
                         first_name=session.get('first_name'))

@app.route('/teacher/resources')
@login_required
@role_required('Teacher')
def teacher_resources():
    """Teacher Resources management page."""
    return render_template('teacher/resources.html',
                         username=session.get('username'),
                         first_name=session.get('first_name'))

@app.route('/teacher/doubts')
@login_required
@role_required('Teacher')
def teacher_doubts_page():
    """Teacher Student Doubts page."""
    return render_template('teacher/doubts.html',
                         username=session.get('username'),
                         first_name=session.get('first_name'))

# Duplicate `teacher_stats` endpoint removed — using `get_teacher_stats` implementation defined earlier.

@app.route('/api/teacher/assignments')
@login_required
@role_required('Teacher')
def get_teacher_assignments():
    """Get all assignments created/managed by this teacher."""
    teacher_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.AssignmentID, a.ExamID, e.ExamName, a.DueDate, a.Status,
                   COUNT(DISTINCT a.StudentID) as StudentCount,
                   SUM(CASE WHEN a.Status = 'Completed' THEN 1 ELSE 0 END) as CompletedCount
            FROM Assignments a
            LEFT JOIN Exams e ON a.ExamID = e.ExamID
            WHERE a.TeacherID = %s
            GROUP BY a.AssignmentID, a.ExamID, e.ExamName, a.DueDate, a.Status
            ORDER BY a.DueDate DESC
        """, (teacher_id,))
        
        assignments = cursor.fetchall()
        result = []
        
        for row in assignments:
            title = row[2] if row[2] else f'Assignment #{row[0]}'
            due = row[3].strftime('%Y-%m-%d') if row[3] else 'No deadline'
            student_count = row[5] or 0
            completed_count = row[6] or 0
            completion_rate = round((completed_count) / (student_count or 1) * 100, 1)
            result.append({
                'assignmentId': row[0],
                'title': title,
                'description': '',
                'dueDate': due,
                'status': row[4],
                'studentCount': int(student_count),
                'completedCount': int(completed_count),
                'completionRate': completion_rate
            })
        
        return jsonify({'assignments': result}), 200

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/teacher/class-analytics')
@login_required
@role_required('Teacher')
def teacher_class_analytics():
    """Get class-wide analytics and performance metrics."""
    teacher_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        
        # Performance distribution (breakdown by score ranges)
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN r.Percentage >= 80 THEN '80-100%'
                    WHEN r.Percentage >= 60 THEN '60-80%'
                    WHEN r.Percentage >= 40 THEN '40-60%'
                    ELSE 'Below 40%'
                END as ScoreRange,
                COUNT(*) as StudentCount
            FROM Results r
            JOIN Assignments a ON r.StudentID = a.StudentID
            WHERE a.TeacherID = %s
            GROUP BY ScoreRange
            ORDER BY ScoreRange DESC
        """, (teacher_id,))
        
        performance_dist = {}
        for row in cursor.fetchall():
            performance_dist[row[0]] = row[1]
        
        # Top performing students
        cursor.execute("""
            SELECT u.FirstName, u.LastName, AVG(r.Percentage) as AvgPercentage
            FROM Results r
            JOIN Assignments a ON r.StudentID = a.StudentID
            JOIN Users u ON r.StudentID = u.UserID
            WHERE a.TeacherID = %s
            GROUP BY r.StudentID, u.FirstName, u.LastName
            ORDER BY AvgPercentage DESC
            LIMIT 5
        """, (teacher_id,))
        
        top_students = [
            {'name': f"{row[0]} {row[1]}", 'avgScore': round(float(row[2]), 2)}
            for row in cursor.fetchall()
        ]
        
        # Assignment completion trend (last 10 assignments)
        cursor.execute("""
            SELECT a.AssignmentID, a.ExamID, e.ExamName, 
                   SUM(CASE WHEN a.Status = 'Completed' THEN 1 ELSE 0 END) as Completed,
                   COUNT(*) as Total,
                   a.CreatedAt
            FROM Assignments a
            LEFT JOIN Exams e ON a.ExamID = e.ExamID
            WHERE a.TeacherID = %s
            GROUP BY a.AssignmentID, a.ExamID, e.ExamName, a.CreatedAt
            ORDER BY a.CreatedAt DESC
            LIMIT 10
        """, (teacher_id,))
        
        assignment_trend = []
        for row in cursor.fetchall():
            # row: AssignmentID, ExamID, ExamName, Completed, Total, CreatedAt
            title = row[2] if row[2] else f"Assignment #{row[0]}"
            completed = row[3] or 0
            total = row[4] or 0
            completion_rate = (completed / total * 100) if total > 0 else 0
            assignment_trend.append({
                'title': title,
                'completed': int(completed),
                'total': int(total),
                'completionRate': round(completion_rate, 1)
            })
        
        return jsonify({
            'performanceDistribution': performance_dist,
            'topStudents': top_students,
            'assignmentTrend': assignment_trend
        }), 200

    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ============================================================================
# ERROR HANDLERS
# ============================================================================
@app.route('/admin/exam-question-counts')
@login_required
def admin_exam_question_counts():
    """Admin diagnostics: show exam list with question counts."""
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.ExamID, e.ExamName, COALESCE(COUNT(q.QuestionID),0) as QCount
            FROM Exams e
            LEFT JOIN Questions q ON e.ExamID = q.ExamID
            GROUP BY e.ExamID, e.ExamName
            ORDER BY e.ExamName ASC
        """)
        rows = cursor.fetchall()
        exams = [{'examID': r[0], 'examName': r[1], 'count': int(r[2])} for r in rows]
    except Exception as e:
        print(f"[admin_exam_question_counts] error: {e}")
        exams = []
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

    return render_template('admin/exam_question_counts.html', exams=exams,
                           username=session.get('username'), first_name=session.get('first_name'))


@app.route('/admin/seed-sample-questions', methods=['POST'])
@login_required
def admin_seed_sample_questions():
    """Seed a small set of sample questions for a given exam_id if count is zero.

    Request JSON: { exam_id: <int>, count: <int, optional default=5> }
    """
    data = request.get_json() if request.is_json else request.form
    try:
        exam_id = int(data.get('exam_id'))
    except Exception:
        return jsonify({'error': 'invalid exam_id'}), 400

    seed_count = int(data.get('count') or 5)

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Questions WHERE ExamID = %s", (exam_id,))
        existing = cursor.fetchone()[0]
        if existing and existing > 0:
            return jsonify({'message': 'Exam already has questions', 'existing': int(existing)}), 200

        samples = []
        for i in range(1, seed_count+1):
            qtext = f"Sample question {i} for exam {exam_id}. What is {i} + {i}?"
            options = [str(i+i), str(i+i+1), str(i+i-1), str(i+i+2)]
            samples.append((exam_id, 'General', qtext, 'Easy', json.dumps(options)))

        insert_sql = """
            INSERT INTO Questions (ExamID, Topic, QuestionText, DifficultyLevel, Options)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_sql, samples)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM Questions WHERE ExamID = %s", (exam_id,))
        new_count = int(cursor.fetchone()[0])
        return jsonify({'message': 'Seeded sample questions', 'new_count': new_count}), 201

    except Exception as e:
        print(f"[admin_seed_sample_questions] error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# ASSIGNMENT SUBMISSION ROUTES
# ============================================================================

@app.route('/api/submit-assignment', methods=['POST'])
@login_required
def submit_assignment():
    """
    Handle assignment submission with file upload.
    Student uploads a file (PDF, DOC, etc.) for their assignment.
    """
    user_id = session.get('user_id')
    assignment_id = request.form.get('assignment_id')
    
    if not assignment_id:
        return jsonify({'error': 'Assignment ID is required'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Allowed file extensions
    allowed_extensions = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'xls', 'xlsx', 'ppt', 'pptx'}
    
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'File type not allowed. Allowed: PDF, DOC, DOCX, TXT, JPG, PNG, XLS, XLSX, PPT, PPTX'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verify assignment belongs to this student
        cursor.execute(
            "SELECT AssignmentID FROM Assignments WHERE AssignmentID = %s AND StudentID = %s",
            (assignment_id, user_id)
        )
        if not cursor.fetchone():
            return jsonify({'error': 'Assignment not found or does not belong to you'}), 403
        
        # Create submissions directory
        submissions_dir = os.path.join('uploads', 'submissions', str(assignment_id))
        os.makedirs(submissions_dir, exist_ok=True)
        
        # Save file with timestamp to avoid conflicts
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        filename = f"{user_id}_{int(time.time())}.{file_ext}"
        filepath = os.path.join(submissions_dir, filename)
        
        file.save(filepath)
        file_size = os.path.getsize(filepath)
        
        # Check if submission already exists
        cursor.execute(
            "SELECT SubmissionID FROM AssignmentSubmissions WHERE AssignmentID = %s AND StudentID = %s",
            (assignment_id, user_id)
        )
        existing_submission = cursor.fetchone()
        
        if existing_submission:
            # Update existing submission
            submission_id = existing_submission[0]
            cursor.execute(
                """UPDATE AssignmentSubmissions 
                   SET FilePath = %s, FileName = %s, FileSize = %s, SubmittedAt = NOW()
                   WHERE SubmissionID = %s""",
                (filepath, original_filename, file_size, submission_id)
            )
            message = 'Assignment updated successfully'
        else:
            # Create new submission
            cursor.execute(
                """INSERT INTO AssignmentSubmissions (AssignmentID, StudentID, FilePath, FileName, FileSize)
                   VALUES (%s, %s, %s, %s, %s)""",
                (assignment_id, user_id, filepath, original_filename, file_size)
            )
            message = 'Assignment submitted successfully'
        
        # Update assignment status to 'Completed'
        cursor.execute(
            "UPDATE Assignments SET Status = 'Completed' WHERE AssignmentID = %s",
            (assignment_id,)
        )
        
        conn.commit()
        
        return jsonify({'message': message, 'filename': original_filename}), 201
    
    except Exception as e:
        print(f"[Assignment Submission] Error: {e}")
        return jsonify({'error': f'Failed to submit assignment: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/student/submissions', methods=['GET'])
@login_required
def get_student_submissions():
    """Get all submissions for the logged-in student."""
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                sub.SubmissionID, 
                sub.AssignmentID,
                a.ExamID,
                e.ExamName,
                sub.FileName,
                sub.SubmittedAt,
                sub.Grade,
                sub.TeacherFeedback,
                a.Status,
                a.DueDate
            FROM AssignmentSubmissions sub
            JOIN Assignments a ON sub.AssignmentID = a.AssignmentID
            JOIN Exams e ON a.ExamID = e.ExamID
            WHERE sub.StudentID = %s
            ORDER BY sub.SubmittedAt DESC
        """, (user_id,))
        
        submissions = cursor.fetchall()
        result = [
            {
                'submissionID': row[0],
                'assignmentID': row[1],
                'examID': row[2],
                'examName': row[3],
                'fileName': row[4],
                'submittedAt': row[5].strftime('%Y-%m-%d %H:%M') if row[5] else '',
                'grade': row[6],
                'feedback': row[7],
                'status': row[8],
                'dueDate': row[9].strftime('%Y-%m-%d') if row[9] else ''
            }
            for row in submissions
        ]
        
        return jsonify({'submissions': result}), 200
    
    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/teacher/submissions/<int:assignment_id>', methods=['GET'])
@login_required
@role_required('Teacher')
def get_assignment_submissions(assignment_id):
    """Get all submissions for a specific assignment (teacher view)."""
    teacher_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verify teacher owns this assignment
        cursor.execute(
            "SELECT AssignmentID FROM Assignments WHERE AssignmentID = %s AND TeacherID = %s",
            (assignment_id, teacher_id)
        )
        if not cursor.fetchone():
            return jsonify({'error': 'Assignment not found or does not belong to you'}), 403
        
        # Get all submissions for this assignment
        cursor.execute("""
            SELECT 
                sub.SubmissionID,
                sub.AssignmentID,
                sub.StudentID,
                u.FirstName,
                u.LastName,
                u.Username,
                sub.FileName,
                sub.FilePath,
                sub.FileSize,
                sub.SubmittedAt,
                sub.Grade,
                sub.TeacherFeedback,
                a.DueDate
            FROM AssignmentSubmissions sub
            JOIN Assignments a ON sub.AssignmentID = a.AssignmentID
            JOIN Users u ON sub.StudentID = u.UserID
            WHERE sub.AssignmentID = %s
            ORDER BY sub.SubmittedAt DESC
        """, (assignment_id,))
        
        submissions = cursor.fetchall()
        result = [
            {
                'submissionID': row[0],
                'assignmentID': row[1],
                'studentID': row[2],
                'studentName': f"{row[3]} {row[4]}",
                'studentUsername': row[5],
                'fileName': row[6],
                'filePath': row[7],
                'fileSize': row[8],
                'submittedAt': row[9].strftime('%Y-%m-%d %H:%M') if row[9] else '',
                'grade': row[10],
                'feedback': row[11],
                'dueDate': row[12].strftime('%Y-%m-%d') if row[12] else ''
            }
            for row in submissions
        ]
        
        return jsonify({'submissions': result}), 200
    
    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/grade-submission/<int:submission_id>', methods=['POST'])
@login_required
@role_required('Teacher')
def grade_submission(submission_id):
    """Grade a student submission with feedback."""
    teacher_id = session.get('user_id')
    data = request.get_json() or {}
    grade = data.get('grade', '').strip()
    feedback = data.get('feedback', '').strip()
    
    if not grade:
        return jsonify({'error': 'Grade is required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verify submission exists and belongs to this teacher's assignment
        cursor.execute("""
            SELECT sub.SubmissionID FROM AssignmentSubmissions sub
            JOIN Assignments a ON sub.AssignmentID = a.AssignmentID
            WHERE sub.SubmissionID = %s AND a.TeacherID = %s
        """, (submission_id, teacher_id))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Submission not found or does not belong to you'}), 403
        
        # Update submission with grade and feedback
        cursor.execute(
            """UPDATE AssignmentSubmissions 
               SET Grade = %s, TeacherFeedback = %s, GradedAt = NOW()
               WHERE SubmissionID = %s""",
            (grade, feedback, submission_id)
        )
        
        conn.commit()
        
        return jsonify({'message': 'Submission graded successfully', 'grade': grade}), 200
    
    except Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/uploads/submissions/<path:filepath>', methods=['GET'])
@login_required
def download_submission(filepath):
    """Download a submission file (with authorization)."""
    user_id = session.get('user_id')
    user_role = session.get('role')
    
    # Reconstruct safe filepath
    safe_path = os.path.join('uploads', 'submissions', filepath)
    
    if not os.path.exists(safe_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Verify user has permission to download
    # Check if user is the student who submitted OR the teacher
    try:
        assignment_id = filepath.split('/')[0]
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Check if user is the student
        cursor.execute(
            "SELECT AssignmentID FROM Assignments WHERE AssignmentID = %s AND StudentID = %s",
            (assignment_id, user_id)
        )
        is_student = cursor.fetchone() is not None
        
        # Check if user is the teacher
        cursor.execute(
            "SELECT AssignmentID FROM Assignments WHERE AssignmentID = %s AND TeacherID = %s",
            (assignment_id, user_id)
        )
        is_teacher = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        
        if not (is_student or is_teacher):
            return jsonify({'error': 'Unauthorized'}), 403
        
        return send_from_directory(os.path.dirname(safe_path), os.path.basename(safe_path))
    
    except Exception as e:
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

# ============================================================================
# RUN APPLICATION
# ============================================================================
# Duplicate `class-analytics` GET handler removed — using earlier `teacher_class_analytics` implementation.

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Run Flask development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

# AI question-generation endpoint removed.
