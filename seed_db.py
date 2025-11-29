"""
Comprehensive test data seeding script for LearnMatrix
Adds students with test results, study metrics, and various achievements
Supports multiple exams: JEE, NEET, CAT
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import bcrypt
from datetime import datetime, timedelta
import random

load_dotenv()

def hash_password(password):
    """Hash password with bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'learnmatrix')
    )
    
    cursor = conn.cursor()
    
    # Clear existing test data (keep schema)
    print("Clearing existing test data...")
    cursor.execute("DELETE FROM ActivityLog")
    cursor.execute("DELETE FROM Achievements")
    cursor.execute("DELETE FROM Results")
    cursor.execute("DELETE FROM Doubts")
    cursor.execute("DELETE FROM Assignments")
    cursor.execute("DELETE FROM Questions")
    cursor.execute("DELETE FROM Exams")
    cursor.execute("DELETE FROM Users WHERE Role = 'Student' OR Role = 'Teacher'")
    
    # Create teachers
    print("\n[TEACHERS] Creating teacher accounts...")
    teacher_username = 'teacher_test'
    teacher_password = hash_password('test123')
    cursor.execute("""
        INSERT INTO Users (Username, Email, PasswordHash, Role, FirstName, LastName)
        VALUES (%s, %s, %s, 'Teacher', 'John', 'Smith')
    """, (teacher_username, 'teacher@learnmatrix.com', teacher_password))
    teacher_id = cursor.lastrowid
    print(f"[OK] Teacher created: {teacher_username} (ID: {teacher_id})")
    
    # Create additional teachers
    additional_teachers = [
        ('prof_sharma', 'Rajesh', 'Sharma'),
        ('dr_patel', 'Priya', 'Patel'),
        ('mrs_gupta', 'Neha', 'Gupta'),
        ('mr_verma', 'Anil', 'Verma'),
        ('dr_singh', 'Karan', 'Singh'),
    ]
    
    teacher_ids = [teacher_id]
    
    for username, first_name, last_name in additional_teachers:
        password_hash = hash_password('test123')
        cursor.execute("""
            INSERT INTO Users (Username, Email, PasswordHash, Role, FirstName, LastName)
            VALUES (%s, %s, %s, 'Teacher', %s, %s)
        """, (username, f'{username}@learnmatrix.com', password_hash, first_name, last_name))
        teacher_ids.append(cursor.lastrowid)
        print(f"[OK] {first_name} {last_name} ({username})")
    
    print(f"\n[OK] Created {len(teacher_ids)} teachers total")
    
    # Create multiple exams: JEE, NEET, CAT
    print("\n[EXAMS] Creating exams...")
    exams_data = [
        ('JEE Main 2025', 'Joint Entrance Examination Main Paper - Engineering Entrance', 90, 180),
        ('NEET 2025', 'National Eligibility cum Entrance Test - Medical Entrance', 180, 200),
        ('CAT 2025', 'Common Admission Test - Management Entrance', 66, 120),
    ]
    
    exam_ids = {}
    exam_topics = {
        'JEE Main 2025': [
            ('Physics', ['Mechanics', 'Thermodynamics', 'Optics', 'Electromagnetism', 'Waves', 'Modern Physics']),
            ('Chemistry', ['Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry', 'Reactions', 'Equilibrium', 'Thermodynamics']),
            ('Mathematics', ['Algebra', 'Trigonometry', 'Calculus', 'Geometry', 'Coordinate Geometry', 'Probability'])
        ],
        'NEET 2025': [
            ('Physics', ['Mechanics', 'Thermodynamics', 'Optics', 'Electromagnetism', 'Modern Physics', 'Waves']),
            ('Chemistry', ['Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry', 'Biomolecules', 'Polymers']),
            ('Biology', ['Botany', 'Zoology', 'Cell Biology', 'Genetics', 'Ecology', 'Human Physiology'])
        ],
        'CAT 2025': [
            ('Quantitative Aptitude', ['Arithmetic', 'Algebra', 'Geometry', 'Number System', 'Percentages', 'Profit & Loss']),
            ('Data Interpretation', ['Tables', 'Charts', 'Graphs', 'Caselets', 'Data Sufficiency']),
            ('Verbal Ability', ['Reading Comprehension', 'Para Jumbles', 'Sentence Correction', 'Vocabulary', 'Critical Reasoning'])
        ]
    }
    
    all_questions = {}
    
    for exam_name, description, total_questions, total_time in exams_data:
        cursor.execute("""
            INSERT INTO Exams (ExamName, Description, TotalQuestions, TotalTime)
            VALUES (%s, %s, %s, %s)
        """, (exam_name, description, total_questions, total_time))
        exam_id = cursor.lastrowid
        exam_ids[exam_name] = exam_id
        print(f"[OK] Exam created: {exam_name} (ID: {exam_id})")
        
        # Create questions for this exam
        questions_for_exam = []
        topics = exam_topics[exam_name]
        
        for subject, subtopics in topics:
            for subtopic in subtopics:
                # Create 6-8 questions per subtopic for rich data
                num_questions = random.randint(6, 8)
                for i in range(num_questions):
                    cursor.execute("""
                        INSERT INTO Questions (ExamID, Topic, SubTopic, QuestionText, Options, CorrectOption, DifficultyLevel)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        exam_id,
                        subject,
                        subtopic,
                        f"{exam_name} - {subject} - {subtopic} Question {i+1}",
                        '["Option A", "Option B", "Option C", "Option D"]',
                        chr(65 + random.randint(0, 3)),
                        random.choice(['Easy', 'Medium', 'Hard'])
                    ))
                    questions_for_exam.append(cursor.lastrowid)
        
        all_questions[exam_name] = questions_for_exam
        print(f"  [OK] Created {len(questions_for_exam)} questions for {exam_name}")
    
    # Create students with realistic data
    print("\n[STUDENTS] Creating student accounts with comprehensive test data...")
    
    student_data = [
        ('akshay_sharma', 'Akshay', 'Sharma'),
        ('priya_verma', 'Priya', 'Verma'),
        ('rahul_patel', 'Rahul', 'Patel'),
        ('neha_singh', 'Neha', 'Singh'),
        ('arjun_kumar', 'Arjun', 'Kumar'),
        ('deepika_gupta', 'Deepika', 'Gupta'),
        ('rohan_desai', 'Rohan', 'Desai'),
        ('anjali_nair', 'Anjali', 'Nair'),
        ('vikram_reddy', 'Vikram', 'Reddy'),
        ('shreya_iyer', 'Shreya', 'Iyer'),
        ('aditya_bhat', 'Aditya', 'Bhat'),
    ]
    
    # Assign exams to students (mix of JEE, NEET, CAT)
    exam_assignments = {
        'JEE Main 2025': [0, 1, 2, 3, 4, 5],  # First 6 students
        'NEET 2025': [6, 7, 8, 9],  # Next 4 students
        'CAT 2025': [10, 11],  # Last 2 students
    }
    
    student_ids = []
    student_exam_map = {}  # Map student index to their primary exam
    
    for idx, (username, first_name, last_name) in enumerate(student_data):
        password_hash = hash_password('test123')
        cursor.execute("""
            INSERT INTO Users (Username, Email, PasswordHash, Role, FirstName, LastName)
            VALUES (%s, %s, %s, 'Student', %s, %s)
        """, (username, f'{username}@learnmatrix.com', password_hash, first_name, last_name))
        student_id = cursor.lastrowid
        student_ids.append(student_id)
        
        # Determine primary exam for this student
        for exam_name, student_indices in exam_assignments.items():
            if idx in student_indices:
                student_exam_map[student_id] = exam_name
                break
        
        print(f"  [OK] {first_name} {last_name} ({username}) - Primary Exam: {student_exam_map.get(student_id, 'JEE Main 2025')}")
    
    print(f"\n[OK] Created {len(student_ids)} students")
    
    # Create multiple assignments per student (some students have multiple exams)
    print("\n[ASSIGNMENTS] Creating comprehensive assignments...")
    assignment_ids = []
    all_assignments = {}  # Track assignments per student
    
    for idx, student_id in enumerate(student_ids):
        # Assign each student to a teacher (distribute evenly)
        teacher = teacher_ids[idx % len(teacher_ids)]
        primary_exam = student_exam_map.get(student_id, 'JEE Main 2025')
        primary_exam_id = exam_ids[primary_exam]
        
        all_assignments[student_id] = []
        
        # Each student gets 1-2 assignments for their primary exam (due to unique constraint)
        num_assignments = random.randint(1, 2)
        for assignment_num in range(num_assignments):
            due_date = (datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
            status = random.choice(['Assigned', 'Started', 'Completed', 'Overdue'])
            
            # Use INSERT IGNORE to handle unique constraint
            cursor.execute("""
                INSERT IGNORE INTO Assignments (TeacherID, StudentID, ExamID, Status, DueDate)
                VALUES (%s, %s, %s, %s, %s)
            """, (teacher, student_id, primary_exam_id, status, due_date))
            if cursor.lastrowid > 0:
                assignment_id = cursor.lastrowid
                assignment_ids.append(assignment_id)
                all_assignments[student_id].append(assignment_id)
        
        # Some students also get assignments for other exams (cross-training)
        if random.random() < 0.3:  # 30% chance
            other_exams = [e for e in exam_ids.keys() if e != primary_exam]
            if other_exams:
                secondary_exam = random.choice(other_exams)
                secondary_exam_id = exam_ids[secondary_exam]
                cursor.execute("""
                    INSERT IGNORE INTO Assignments (TeacherID, StudentID, ExamID, Status, DueDate)
                    VALUES (%s, %s, %s, %s, %s)
                """, (teacher, student_id, secondary_exam_id, 'Assigned', 
                      (datetime.now() + timedelta(days=random.randint(15, 45))).strftime('%Y-%m-%d')))
                if cursor.lastrowid > 0:
                    assignment_ids.append(cursor.lastrowid)
                    all_assignments[student_id].append(cursor.lastrowid)
    
    print(f"[OK] Created {len(assignment_ids)} assignments across all students")
    
    # Add comprehensive test results for each student
    print("\n[RESULTS] Adding comprehensive test results and performance data...")
    
    total_results = 0
    for student_id in student_ids:
        primary_exam = student_exam_map.get(student_id, 'JEE Main 2025')
        primary_exam_id = exam_ids[primary_exam]
        student_assignments = all_assignments.get(student_id, [])
        
        if not student_assignments:
            continue
        
        # Each student takes 18-25 tests for rich analytics
        num_tests = random.randint(18, 25)
        
        for test_num in range(num_tests):
            assignment_id = random.choice(student_assignments)
            
            # Get exam details for this assignment
            cursor.execute("SELECT ExamID FROM Assignments WHERE AssignmentID = %s", (assignment_id,))
            result = cursor.fetchone()
            if not result:
                continue
            exam_id_for_result = result[0]
            
            # Get exam name to determine topics
            cursor.execute("SELECT ExamName FROM Exams WHERE ExamID = %s", (exam_id_for_result,))
            exam_name_result = cursor.fetchone()
            exam_name_for_result = exam_name_result[0] if exam_name_result else primary_exam
            
            # Create improvement curve over time
            base_score = random.randint(35, 70)
            improvement = (test_num / num_tests) * 25  # Improvement over attempts
            percentage = min(97, base_score + improvement + random.randint(-12, 12))
            percentage = max(22, percentage)
            
            # Get total questions for this exam
            cursor.execute("SELECT TotalQuestions FROM Exams WHERE ExamID = %s", (exam_id_for_result,))
            total_q_result = cursor.fetchone()
            total_questions = total_q_result[0] if total_q_result else 90
            
            # Random time spent (in seconds)
            time_spent = random.randint(3500, 13000)
            correct_answers = int((percentage / 100) * total_questions)
            
            # Determine topic based on exam
            if exam_name_for_result == 'NEET 2025':
                topic = random.choice(['Physics', 'Chemistry', 'Biology'])
            elif exam_name_for_result == 'CAT 2025':
                topic = random.choice(['Quantitative Aptitude', 'Data Interpretation', 'Verbal Ability'])
            else:  # JEE
                topic = random.choice(['Physics', 'Chemistry', 'Mathematics'])
            
            # Create result with timestamp spread over past 4 months
            days_ago = random.randint(0, 120)
            result_date = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            cursor.execute("""
                INSERT INTO Results (AssignmentID, StudentID, Score, TotalQuestions, Percentage, CompletionTime, Topic, Timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                assignment_id,
                student_id,
                correct_answers,
                total_questions,
                percentage,
                time_spent,
                topic,
                result_date.strftime('%Y-%m-%d %H:%M:%S')
            ))
            total_results += 1
        
        # Add extensive activity logs (40-60 per student for rich analytics)
        num_activities = random.randint(40, 60)
        for log_num in range(num_activities):
            activity_type = random.choice(['Login', 'TestStart', 'TestSubmit', 'FocusSession', 'ViewedResources'])
            
            # Different activity types have different typical durations
            if activity_type == 'FocusSession':
                duration = random.randint(600, 4200)  # 10 mins to 70 mins
            elif activity_type in ['TestStart', 'TestSubmit']:
                duration = random.randint(1800, 9000)  # 30 mins to 2.5 hours
            elif activity_type == 'ViewedResources':
                duration = random.randint(300, 2400)  # 5 to 40 mins
            else:  # Login
                duration = random.randint(30, 300)  # 30 seconds to 5 mins
            
            # Use primary exam for activity log
            # Spread activities over past 4 months
            days_ago = random.randint(0, 120)
            activity_date = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            cursor.execute("""
                INSERT INTO ActivityLog (UserID, ActivityType, Duration, ExamID, Timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                student_id,
                activity_type,
                duration,
                primary_exam_id,
                activity_date.strftime('%Y-%m-%d %H:%M:%S')
            ))
    
    print(f"[OK] Added {total_results} test results and 40-60 activity logs per student")
    
    # Add comprehensive achievements
    print("\n[ACHIEVEMENTS] Adding comprehensive achievements...")
    
    achievement_types = [
        ('Focused Learner', 'Completed 5+ hours of focused study sessions', 100),
        ('Consistent', '7 consecutive days of login', 75),
        ('High Scorer', 'Scored 90% or higher on a test', 150),
        ('Problem Solver', 'Cleared 5+ doubts', 80),
        ('Study Marathon', '10 hours of study completed', 120),
        ('Quick Learner', 'Completed test in under 120 minutes', 60),
        ('Math Genius', 'Perfect score in Mathematics', 120),
        ('Chemistry Master', 'Perfect score in Chemistry', 120),
        ('Physics Pro', 'Perfect score in Physics', 120),
        ('Biology Expert', 'Perfect score in Biology', 120),
        ('Rising Star', 'Improved score by 20% consecutively', 110),
        ('Night Owl', 'Completed 10 focus sessions', 70),
        ('Speed Demon', 'Completed test in under 90 minutes', 90),
        ('Comeback Kid', 'Improved from lowest to highest score', 130),
        ('Perfect Week', '100% completion rate for a week', 100),
        ('Dedicated Student', '20+ test attempts', 85),
    ]
    
    total_achievements = 0
    for student_id in student_ids:
        # Randomly assign 4-8 achievements to each student
        num_achievements = random.randint(4, 8)
        selected_achievements = random.sample(achievement_types, min(num_achievements, len(achievement_types)))
        
        for trophy_name, description, points in selected_achievements:
            # Add achievements with timestamps spread over past 120 days
            days_ago = random.randint(0, 120)
            achievement_date = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute("""
                INSERT IGNORE INTO Achievements (StudentID, TrophyName, Description, Points, DateEarned)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                student_id,
                trophy_name,
                description,
                points,
                achievement_date.strftime('%Y-%m-%d')
            ))
            total_achievements += 1
    
    print(f"[OK] Added {total_achievements} achievements total (4-8 per student)")
    
    # Add comprehensive doubts from students
    print("\n[DOUBTS] Adding comprehensive student doubts...")
    
    doubt_topics_jee = [
        'Circular Motion', 'Heat and Thermodynamics', 'Organic Reactions', 'Integration',
        'Trigonometric Identities', 'Electrochemistry', 'Vectors', 'Atomic Structure',
        'Quantum Mechanics', 'Electrode Potential', 'Logarithms', 'Complex Numbers',
    ]
    
    doubt_topics_neet = [
        'Cell Biology', 'Genetics', 'Human Physiology', 'Plant Kingdom',
        'Animal Kingdom', 'Ecology', 'Biomolecules', 'Photosynthesis',
        'Respiration', 'Nervous System', 'Circulatory System', 'Reproduction',
    ]
    
    doubt_topics_cat = [
        'Profit and Loss', 'Time and Work', 'Permutations', 'Probability',
        'Reading Comprehension', 'Para Jumbles', 'Data Sufficiency', 'Caselets',
        'Percentages', 'Ratio and Proportion', 'Time Speed Distance', 'Number System',
    ]
    
    doubt_texts = [
        "Can you explain the concept of {topic}? I'm struggling with this.",
        "How do I approach problems related to {topic}?",
        "I don't understand the difference between A and B in {topic}. Please help!",
        "Could you provide more examples for {topic}?",
        "My calculation for {topic} is wrong. Can you review it?",
        "Is there a shortcut or trick for solving {topic} quickly?",
        "I'm confused about the derivation in {topic}. Can you clarify?",
        "How is {topic} applied in real-world scenarios?",
    ]
    
    doubt_ids = []
    for student_id in student_ids:
        primary_exam = student_exam_map.get(student_id, 'JEE Main 2025')
        
        # Select appropriate doubt topics based on exam
        if primary_exam == 'NEET 2025':
            available_topics = doubt_topics_neet
        elif primary_exam == 'CAT 2025':
            available_topics = doubt_topics_cat
        else:
            available_topics = doubt_topics_jee
        
        # Each student has 3-6 doubts
        num_doubts = random.randint(3, 6)
        for _ in range(num_doubts):
            topic = random.choice(available_topics)
            doubt_text = random.choice(doubt_texts).format(topic=topic)
            status = random.choice(['Pending', 'In_Progress', 'Cleared'])
            
            # Spread doubts over past 4 months
            days_ago = random.randint(0, 120)
            doubt_date = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute("""
                INSERT INTO Doubts (StudentID, Topic, DoubtText, Status, Priority, Timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                topic,
                doubt_text,
                status,
                random.choice(['Low', 'Medium', 'High']),
                doubt_date.strftime('%Y-%m-%d %H:%M:%S')
            ))
            doubt_ids.append(cursor.lastrowid)
    
    # Assign doubts to teachers for resolution
    resolved_count = 0
    for doubt_id in doubt_ids:
        # 60% of doubts are resolved
        if random.random() < 0.6:
            cursor.execute("""
                SELECT Status FROM Doubts WHERE DoubtID = %s
            """, (doubt_id,))
            status = cursor.fetchone()[0]
            
            if status == 'Pending':
                # Update to Cleared with resolution
                resolution_texts = [
                    "Great question! Here's a detailed explanation: The concept involves understanding the fundamental principles and applying them systematically.",
                    "Thank you for asking! Let me break this down: First, we need to understand the basic concept, then we can apply it to solve problems.",
                    "Excellent question! The key to mastering this topic is to practice regularly and understand the underlying principles.",
                ]
                resolution_text = random.choice(resolution_texts)
                cursor.execute("""
                    UPDATE Doubts 
                    SET TeacherID = %s, ResolutionText = %s, Status = 'Cleared', ResolvedAt = NOW()
                    WHERE DoubtID = %s
                """, (random.choice(teacher_ids), resolution_text, doubt_id))
                resolved_count += 1
    
    print(f"[OK] Added {len(doubt_ids)} doubts ({resolved_count} resolved)")
    
    conn.commit()
    
    print("\n" + "="*60)
    print("[SUCCESS] DATABASE SEEDING COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n[SUMMARY]:")
    print(f"  • Teachers: {len(teacher_ids)}")
    print(f"  • Students: {len(student_ids)}")
    print(f"  • Exams: {len(exam_ids)} (JEE Main 2025, NEET 2025, CAT 2025)")
    print(f"  • Questions: {sum(len(q) for q in all_questions.values())} total")
    print(f"  • Assignments: {len(assignment_ids)} (2-4 per student, some with multiple exams)")
    print(f"  • Test Results: {total_results} (18-25 per student)")
    print(f"  • Activity Logs: 40-60 per student")
    print(f"  • Achievements: {total_achievements} (4-8 per student)")
    print(f"  • Doubts: {len(doubt_ids)} (3-6 per student, {resolved_count} resolved)")
    print("\n[EXAM DISTRIBUTION]:")
    print(f"  • JEE Main 2025: {len(exam_assignments['JEE Main 2025'])} students")
    print(f"  • NEET 2025: {len(exam_assignments['NEET 2025'])} students")
    print(f"  • CAT 2025: {len(exam_assignments['CAT 2025'])} students")
    print("\n[PASSWORD] All test accounts use password: test123")
    print("\n[STUDENT ACCOUNTS]:")
    for idx, (username, first_name, last_name) in enumerate(student_data):
        exam = student_exam_map.get(student_ids[idx], 'JEE Main 2025')
        print(f"  • {username} ({first_name} {last_name}) - {exam}")
    print("\n[TEACHER ACCOUNTS]:")
    for username, first_name, last_name in ([('teacher_test', 'John', 'Smith')] + additional_teachers):
        print(f"  • {username} ({first_name} {last_name})")
    print()
    
    cursor.close()
    conn.close()
    
except Error as err:
    print(f"\n[ERROR] Error: {err}")
    import traceback
    traceback.print_exc()
