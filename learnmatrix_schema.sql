-- LearnMatrix: Personalized & Gamified Entrance Exam Learning System
-- Complete MySQL Database Schema (DDL)
-- Created: November 18, 2025

-- ============================================================================
-- DROP EXISTING TABLES (for fresh setup)
-- ============================================================================
DROP TABLE IF EXISTS Achievements;
DROP TABLE IF EXISTS ActivityLog;
DROP TABLE IF EXISTS Doubts;
DROP TABLE IF EXISTS Results;
DROP TABLE IF EXISTS Assignments;
DROP TABLE IF EXISTS Questions;
DROP TABLE IF EXISTS Exams;
DROP TABLE IF EXISTS Users;

-- ============================================================================
-- 1. USERS TABLE - Authentication and Role Management
-- ============================================================================
CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(100) NOT NULL UNIQUE,
    Email VARCHAR(255) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    Role ENUM('Student', 'Teacher', 'Admin') NOT NULL DEFAULT 'Student',
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    LastLogin TIMESTAMP NULL,
    IsActive TINYINT(1) DEFAULT 1,
    
    INDEX idx_username (Username),
    INDEX idx_email (Email),
    INDEX idx_role (Role),
    INDEX idx_last_login (LastLogin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 2. EXAMS TABLE - Entrance Exam Definitions
-- ============================================================================
CREATE TABLE Exams (
    ExamID INT AUTO_INCREMENT PRIMARY KEY,
    ExamName VARCHAR(255) NOT NULL UNIQUE,
    Description TEXT,
    TotalQuestions INT NOT NULL DEFAULT 0,
    TotalTime INT DEFAULT NULL COMMENT 'in minutes',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_exam_name (ExamName)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 3. QUESTIONS TABLE - Question Papers/Data Storage
-- ============================================================================
CREATE TABLE Questions (
    QuestionID INT AUTO_INCREMENT PRIMARY KEY,
    ExamID INT NOT NULL,
    Topic VARCHAR(100) NOT NULL,
    SubTopic VARCHAR(100),
    Year INT,
    QuestionText LONGTEXT NOT NULL,
    Options JSON NOT NULL COMMENT 'Stores as JSON array: ["Option A", "Option B", "Option C", "Option D"]',
    CorrectOption VARCHAR(1) NOT NULL COMMENT 'A, B, C, D',
    Explanation TEXT,
    TeacherID INT,
    DifficultyLevel ENUM('Easy', 'Medium', 'Hard') DEFAULT 'Medium',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (ExamID) REFERENCES Exams(ExamID) ON DELETE CASCADE,
    FOREIGN KEY (TeacherID) REFERENCES Users(UserID) ON DELETE SET NULL,
    
    INDEX idx_exam_topic (ExamID, Topic),
    INDEX idx_topic (Topic),
    INDEX idx_subtopic (SubTopic),
    INDEX idx_year (Year),
    INDEX idx_teacher (TeacherID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4. ASSIGNMENTS TABLE - Links Students to Tests
-- ============================================================================
CREATE TABLE Assignments (
    AssignmentID INT AUTO_INCREMENT PRIMARY KEY,
    TeacherID INT NOT NULL,
    StudentID INT NOT NULL,
    ExamID INT NOT NULL,
    Status ENUM('Assigned', 'Started', 'Completed', 'Overdue') NOT NULL DEFAULT 'Assigned',
    DueDate DATETIME,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (TeacherID) REFERENCES Users(UserID) ON DELETE CASCADE,
    FOREIGN KEY (StudentID) REFERENCES Users(UserID) ON DELETE CASCADE,
    FOREIGN KEY (ExamID) REFERENCES Exams(ExamID) ON DELETE CASCADE,
    
    INDEX idx_teacher_assignments (TeacherID),
    INDEX idx_student_assignments (StudentID),
    INDEX idx_exam_assignments (ExamID),
    INDEX idx_status (Status),
    UNIQUE KEY unique_assignment (TeacherID, StudentID, ExamID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4B. ASSIGNMENT_SUBMISSIONS TABLE - Student Assignment File Submissions
-- ============================================================================
CREATE TABLE AssignmentSubmissions (
    SubmissionID INT AUTO_INCREMENT PRIMARY KEY,
    AssignmentID INT NOT NULL,
    StudentID INT NOT NULL,
    FilePath VARCHAR(500) NOT NULL,
    FileName VARCHAR(255) NOT NULL,
    FileSize INT COMMENT 'in bytes',
    SubmittedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Grade VARCHAR(2) COMMENT 'A+, A, B+, B, C, etc.',
    TeacherFeedback LONGTEXT,
    GradedAt TIMESTAMP NULL,
    
    FOREIGN KEY (AssignmentID) REFERENCES Assignments(AssignmentID) ON DELETE CASCADE,
    FOREIGN KEY (StudentID) REFERENCES Users(UserID) ON DELETE CASCADE,
    
    INDEX idx_assignment_submissions (AssignmentID),
    INDEX idx_student_submissions (StudentID),
    INDEX idx_submitted_at (SubmittedAt),
    UNIQUE KEY unique_assignment_submission (AssignmentID, StudentID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 5. RESULTS TABLE - Individual Test Performance Metrics
-- ============================================================================
CREATE TABLE Results (
    ResultID INT AUTO_INCREMENT PRIMARY KEY,
    AssignmentID INT NOT NULL,
    StudentID INT NOT NULL,
    Score INT NOT NULL COMMENT 'Number of correct answers',
    TotalQuestions INT NOT NULL,
    Percentage DECIMAL(5, 2) NOT NULL COMMENT 'Score percentage',
    CompletionTime INT COMMENT 'in seconds',
    Topic VARCHAR(100),
    SubTopic VARCHAR(100),
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (AssignmentID) REFERENCES Assignments(AssignmentID) ON DELETE CASCADE,
    FOREIGN KEY (StudentID) REFERENCES Users(UserID) ON DELETE CASCADE,
    
    INDEX idx_student_results (StudentID),
    INDEX idx_assignment_results (AssignmentID),
    INDEX idx_topic_results (Topic),
    INDEX idx_timestamp (Timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 6. DOUBTS TABLE - Student-Teacher Communication Queue
-- ============================================================================
CREATE TABLE Doubts (
    DoubtID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    TeacherID INT,
    QuestionID INT,
    Topic VARCHAR(100) NOT NULL,
    DoubtText LONGTEXT NOT NULL,
    ImagePath VARCHAR(255),
    Status ENUM('Pending', 'In_Progress', 'Cleared') NOT NULL DEFAULT 'Pending',
    ResolutionText LONGTEXT,
    Priority ENUM('Low', 'Medium', 'High') DEFAULT 'Medium',
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ResolvedAt TIMESTAMP NULL,
    
    FOREIGN KEY (StudentID) REFERENCES Users(UserID) ON DELETE CASCADE,
    FOREIGN KEY (TeacherID) REFERENCES Users(UserID) ON DELETE SET NULL,
    FOREIGN KEY (QuestionID) REFERENCES Questions(QuestionID) ON DELETE SET NULL,
    
    INDEX idx_student_doubts (StudentID),
    INDEX idx_teacher_doubts (TeacherID),
    INDEX idx_status (Status),
    INDEX idx_topic_doubts (Topic),
    INDEX idx_timestamp (Timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 7. ACTIVITYLOG TABLE - Track Study Time and Website Usage
-- ============================================================================
CREATE TABLE ActivityLog (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    ActivityType ENUM('Login', 'Logout', 'TestStart', 'TestSubmit', 'FocusSession', 'DoubtsSubmitted', 'ViewedResources') NOT NULL,
    Duration INT COMMENT 'in seconds',
    ExamID INT,
    AssignmentID INT,
    Details JSON COMMENT 'Additional metadata as JSON',
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    FOREIGN KEY (ExamID) REFERENCES Exams(ExamID) ON DELETE SET NULL,
    FOREIGN KEY (AssignmentID) REFERENCES Assignments(AssignmentID) ON DELETE SET NULL,
    
    INDEX idx_user_activity (UserID),
    INDEX idx_activity_type (ActivityType),
    INDEX idx_timestamp (Timestamp),
    INDEX idx_user_timestamp (UserID, Timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 8. ACHIEVEMENTS TABLE - Gamification Trophies
-- ============================================================================
CREATE TABLE Achievements (
    AchievementID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    TrophyName VARCHAR(100) NOT NULL,
    Description TEXT,
    Badge VARCHAR(50) COMMENT 'Badge type/icon identifier',
    Points INT DEFAULT 0 COMMENT 'Gamification points',
    DateEarned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (StudentID) REFERENCES Users(UserID) ON DELETE CASCADE,
    
    INDEX idx_student_achievements (StudentID),
    INDEX idx_trophy_name (TrophyName),
    INDEX idx_date_earned (DateEarned),
    UNIQUE KEY unique_student_trophy (StudentID, TrophyName)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SAMPLE DATA INSERTION (Optional - for testing)
-- Note: Use seed_db.py script to populate comprehensive test data
-- ============================================================================

-- Sample Exams (Run seed_db.py to get full data with questions)
-- INSERT INTO Exams (ExamName, Description, TotalQuestions, TotalTime)
-- VALUES 
-- ('JEE Main 2025', 'Joint Entrance Examination Main Paper - Engineering Entrance', 90, 180),
-- ('NEET 2025', 'National Eligibility cum Entrance Test - Medical Entrance', 180, 200),
-- ('CAT 2025', 'Common Admission Test - Management Entrance', 66, 120);

-- Sample Teacher Accounts (Password: test123)
-- teacher_test (John Smith)
-- prof_sharma (Rajesh Sharma)
-- dr_patel (Priya Patel)
-- mrs_gupta (Neha Gupta)
-- mr_verma (Anil Verma)
-- dr_singh (Karan Singh)

-- demo_student (Student Test)
-- neha_singh (Neha Singh)
-- arjun_kumar (Arjun Kumar)

-- NEET 2025 Students:
-- deepika_gupta (Deepika Gupta)
-- rohan_desai (Rohan Desai)
-- anjali_nair (Anjali Nair)
-- vikram_reddy (Vikram Reddy)

-- CAT 2025 Students:
-- shreya_iyer (Shreya Iyer)
-- aditya_bhat (Aditya Bhat)

-- To populate full database with comprehensive test data, run:
-- python seed_db.py
