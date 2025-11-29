# LearnMatrix: Personalized & Gamified Entrance Exam Learning System

## 🎓 Project Overview

LearnMatrix is a comprehensive, full-stack web application designed for managing entrance exam preparation with advanced personalization, gamification, and teacher oversight. Built with Python Flask, MySQL, and premium frontend technologies.

### Key Features

✅ **Personalized Learning Paths** - Adaptive weakness topic drilling based on performance analytics
✅ **Gamification System** - Achievement badges, trophies, and engagement scoring
✅ **Real-time Analytics** - Student performance tracking, engagement metrics, and effectiveness analysis
✅ **Dual Portal System** - Separate student and teacher dashboards with role-based access
✅ **Premium UI/UX** - Dark mode first, modern design with Chart.js visualizations
✅ **Secure Authentication** - Bcrypt password hashing, session management
✅ **Scalable Architecture** - Relational database with proper indexing and constraints

---

## 🏗️ Project Structure

```
cs prjct/
├── app.py                          # Core Flask application
├── learnmatrix_schema.sql          # MySQL database DDL
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (create this)
├── config.py                       # Configuration settings
├── templates/
│   ├── base.html                   # Base template with sidebar & topbar
│   ├── login.html                  # Authentication - Login
│   ├── register.html               # Authentication - Registration
│   ├── student/
│   │   └── dashboard.html          # Student portal main page
│   └── teacher/
│       └── dashboard.html          # Teacher portal main page
├── static/
│   ├── css/
│   │   └── premium-styles.css      # Consolidated premium styles
│   └── js/
│       ├── charts.js               # Chart.js initialization
│       └── utils.js                # Utility functions
└── README.md                       # This file
```

---

## 📋 Technology Stack

### Backend
- **Python 3.8+** with Flask web framework
- **MySQL 5.7+** for relational database
- **Bcrypt** for password hashing
- **Flask-Session** for session management
- **mysql-connector-python** for database connectivity

### Frontend
- **HTML5** semantic markup
- **CSS3** with Grid/Flexbox layouts
- **Chart.js** for interactive data visualizations
- **Vanilla JavaScript** (ES6+) for interactivity
- **Responsive Design** (Mobile-first approach)

### Design System
- **Color Palette**: Dark mode (Charcoal, Deep Indigo, Neon Gold, Electric Blue)
- **Typography**: Inter, Poppins sans-serif
- **Animations**: Smooth transitions and hover effects
- **Layout**: Sidebar navigation + responsive grid system

---

## 🗄️ Database Schema (8 Tables)

### 1. **Users**
Manages user authentication and role assignment.
```sql
- UserID (PK)
- Username (UNIQUE)
- Email (UNIQUE)
- PasswordHash
- Role (Student | Teacher | Admin)
- FirstName, LastName
- LastLogin, CreatedAt
- IsActive
```

### 2. **Exams**
Defines entrance exams and their metadata.
```sql
- ExamID (PK)
- ExamName (UNIQUE)
- Description
- TotalQuestions, TotalTime
- CreatedAt, UpdatedAt
```

### 3. **Questions**
Stores question papers with complete metadata.
```sql
- QuestionID (PK)
- ExamID (FK)
- Topic, SubTopic
- Year
- QuestionText, Options (JSON), CorrectOption
- TeacherID (FK)
- DifficultyLevel (Easy | Medium | Hard)
- Explanation
```

### 4. **Assignments**
Links students to tests assigned by teachers.
```sql
- AssignmentID (PK)
- TeacherID (FK), StudentID (FK), ExamID (FK)
- Status (Assigned | Started | Completed | Overdue)
- DueDate
- CreatedAt, UpdatedAt
```

### 5. **Results**
Stores individual test performance metrics.
```sql
- ResultID (PK)
- AssignmentID (FK), StudentID (FK)
- Score, TotalQuestions, Percentage
- CompletionTime (seconds)
- Topic, SubTopic
- Timestamp
```

### 6. **Doubts**
Student-Teacher communication queue for clarifications.
```sql
- DoubtID (PK)
- StudentID (FK), TeacherID (FK)
- QuestionID (FK, nullable)
- Topic, DoubtText
- Status (Pending | In_Progress | Cleared)
- ResolutionText
- Priority (Low | Medium | High)
- Timestamp, ResolvedAt
```

### 7. **ActivityLog**
Tracks study time and website usage patterns.
```sql
- LogID (PK)
- UserID (FK)
- ActivityType (Login | TestStart | FocusSession | etc.)
- Duration (seconds, nullable)
- ExamID (FK), AssignmentID (FK)
- Details (JSON)
- Timestamp
```

### 8. **Achievements**
Manages gamification trophies and badges.
```sql
- AchievementID (PK)
- StudentID (FK)
- TrophyName (UNIQUE per student)
- Description, Badge, Points
- DateEarned
```

---

## 🔐 Core API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login with session creation
- `GET /logout` - User logout and session destruction

### Student Portal
- `GET /student/dashboard` - Main dashboard
- `GET /api/student/weakness-topics` - Identify weakest topics
- `GET /student/focus-session/<exam_id>` - Fetch 10 random questions from weak topics
- `POST /api/log-activity` - Log study sessions and activities
- `POST /student/submit-doubt` - Submit doubt for teacher resolution
- `GET /api/student/performance` - Get performance analytics for charts

### Teacher Portal
- `GET /teacher/dashboard` - Main analytics dashboard
- `GET /api/teacher/student-roster` - Get all students with engagement scores
- `POST /api/teacher/assignment/create` - Create assignments for students
- `POST /api/teacher/analysis/question-effectiveness` - Get question performance analysis
- `GET /api/teacher/doubts-frequency` - Get heatmap of doubted topics

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- MySQL Server 5.7+ (or MariaDB 10.3+)
- pip (Python package manager)

### Step 1: Clone/Create Project Directory
```bash
cd c:\Users\iamab\OneDrive\Desktop\cs prjct
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Create MySQL Database
```sql
-- Open MySQL command line
mysql -u root -p

-- Create database
CREATE DATABASE learnmatrix CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Execute DDL script
mysql -u root -p learnmatrix < learnmatrix_schema.sql
```

### Step 4: Configure Environment Variables
Create `.env` file in project root:
```env
# Flask Configuration
SECRET_KEY=your-secure-random-key-here-change-in-production
FLASK_ENV=development
DEBUG=True

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=learnmatrix

# Session Configuration
SESSION_PERMANENT=True
PERMANENT_SESSION_LIFETIME=604800  # 7 days in seconds
```

### Step 5: Run the Application
```bash
python app.py
```

Application will be available at: `http://localhost:5000`

---

## 📊 Key Features Deep Dive

### 1. **Weakness Topic Drill**
Automatically identifies the student's two weakest topics based on historical test results and presents 10 random questions from those areas for targeted practice.

**Logic**:
```python
# Query Results table, GROUP BY Topic
# Calculate AVG(Percentage) per topic
# ORDER BY AVG_percentage ASC
# LIMIT 2 weakest topics
# Fetch 10 random questions from those topics
```

### 2. **Engagement Score Calculation** (Teachers)
Composite metric: 
```
Engagement Score = (StudyHours × 0.3) + (CompletionRate × 0.4) + (TrophyCount × 0.3)
```
- **Study Hours**: Sum of FocusSession durations in ActivityLog
- **Completion Rate**: % of assigned tests completed
- **Trophy Count**: Number of achievements earned

### 3. **Question Effectiveness Analysis**
Analyzes each question's difficulty and teaching effectiveness:
- **Success Rate**: % of students who scored ≥50% on tests containing the question
- **Avg Completion Time**: Average time spent on the question
- **Difficulty Classification**: 
  - Easy (Success Rate ≥ 70%)
  - Medium (Success Rate 30-70%)
  - Hard (Success Rate < 30%)

### 4. **Gamification System**
Automatically awards badges based on achievement criteria:
- **Focused Learner**: 5+ hours study in a week
- **Consistent**: 7 consecutive days of login
- **High Scorer**: 90%+ on any test
- **Problem Solver**: Cleared 5+ doubts

### 5. **Activity Logging**
Captures all user interactions for analytics:
- Login/Logout
- Test Start/Submit
- Focus Session Start/End
- Doubt Submissions
- Resource Views

---

## 🎨 Premium UI/UX Design Highlights

### Dark Mode First
- Primary: #0f172a (Charcoal Black)
- Secondary: #1e293b (Dark Slate)
- Accent Gold: #fbbf24 (Primary action color)
- Accent Blue: #3b82f6 (Secondary/info)
- Text: #f1f5f9 (Off-white)

### Typography
- **Display**: Inter 700 (28px for titles)
- **Body**: Inter 400 (14px standard)
- **Labels**: Inter 600 (13px uppercase)
- **Professional sans-serif**: Poppins fallback

### Component Design
- **Cards**: Subtle border, hover lift effect
- **Buttons**: Gradient backgrounds, smooth transitions
- **Sidebar**: Fixed navigation with active states
- **Topbar**: Sticky, user profile dropdown
- **Responsive**: Mobile-first grid system

### Animations
- Slide-in on page load
- Hover elevation (2-4px lift)
- Smooth color transitions (0.3s)
- Loading spinners for async operations

---

## 🔒 Security Measures

1. **Password Security**
   - Bcrypt hashing with 12-round salt cost
   - Minimum 8 characters enforced
   - No plain-text storage

2. **Session Management**
   - Server-side Flask sessions
   - 7-day expiration
   - Login-required decorators on protected routes

3. **Input Validation**
   - Email format validation
   - Username/Email uniqueness checks
   - SQL injection prevention via parameterized queries

4. **Database Security**
   - Foreign key constraints
   - Unique constraints on sensitive fields
   - Proper indexing for query performance

---

## 📈 Performance Optimization

### Database
- **Indexes**: On foreign keys, timestamps, frequently filtered columns
- **Query Optimization**: Proper JOINs, GROUP BY aggregations
- **Connection Pooling**: Reusable database connections

### Frontend
- **Chart.js**: Efficient canvas-based rendering
- **Lazy Loading**: Images and data loaded on-demand
- **Responsive Images**: CSS Grid/Flexbox reduces reflows
- **CDN**: Chart.js from jsDelivr CDN

### Caching (Future Enhancement)
- Redis for session caching
- HTTP cache headers for static assets
- Query result caching for analytics

---

## 🧪 Testing Recommendations

### Unit Tests
```python
# test_auth.py - Password hashing, login logic
# test_calculations.py - Engagement score, weakness drill
# test_database.py - CRUD operations
```

### Integration Tests
- API endpoint testing with actual database
- Session persistence validation
- Multi-user concurrent access

### UI/UX Testing
- Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- Mobile responsiveness (320px, 768px, 1024px breakpoints)
- Accessibility (WCAG 2.1 AA compliance)

---

## 🚀 Deployment

### Recommended Platforms
- **Backend**: AWS EC2, Google Cloud Compute, DigitalOcean
- **Database**: AWS RDS, Google Cloud SQL, DigitalOcean Managed Database
- **Frontend Hosting**: Vercel (if separated), Netlify

### Production Checklist
- [ ] Enable HTTPS/SSL certificates
- [ ] Set strong `SECRET_KEY` environment variable
- [ ] Use production-grade WSGI server (Gunicorn, uWSGI)
- [ ] Enable error logging and monitoring (Sentry)
- [ ] Set up automated backups (database, code)
- [ ] Configure firewall rules
- [ ] Implement rate limiting
- [ ] Add 2FA for admin accounts

---

## 📝 Future Enhancements

1. **AI-Powered Recommendations**
   - ML model for personalized question recommendations
   - Predictive analytics for exam performance

2. **Mobile App**
   - React Native or Flutter implementation
   - Offline study mode with sync

3. **Advanced Analytics**
   - Student learning curve visualization
   - Concept mastery tracking
   - Comparative analysis between cohorts

4. **Collaboration Features**
   - Study groups
   - Peer learning Q&A
   - Teacher-to-teacher resource sharing

5. **Integration**
   - LMS integrations (Moodle, Canvas, Blackboard)
   - Video platform integration (YouTube, Vimeo)
   - Calendar sync (Google Calendar, Outlook)

---

## 🤝 Support & Contribution

For issues, bug reports, or feature requests, please contact the development team.

---

## 📄 License

© 2024 LearnMatrix. All rights reserved. Proprietary software.

---

**Last Updated**: November 18, 2025
**Version**: 1.0.0
