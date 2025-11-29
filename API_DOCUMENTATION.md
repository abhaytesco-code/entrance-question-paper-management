# LearnMatrix API Documentation

## 📡 Base URL
```
http://localhost:5000
```

## 🔑 Authentication
All protected endpoints require an active session. Log in first via `/login` to obtain session cookies.

---

## 🔐 Authentication Endpoints

### POST /register
**Register a new user account**

**Request:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "Student"  // "Student" or "Teacher"
}
```

**Response (201 Created):**
```json
{
  "message": "Registration successful! Please login."
}
```

**Status Codes:**
- `201`: Registration successful
- `400`: Missing fields or invalid input
- `500`: Database error

---

### POST /login
**Authenticate user and create session**

**Request:**
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "redirect": "/student/dashboard"
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "Invalid username or password"
}
```

---

### GET /logout
**Destroy user session and logout**

**Response (302 Redirect):**
Redirects to `/login`

---

## 👨‍🎓 Student Portal Endpoints

### GET /student/dashboard
**Load student main dashboard page**

**Response:** HTML page with embedded JavaScript for data loading

---

### GET /api/student/weakness-topics
**Identify student's two weakest topics based on test results**

**Response (200 OK):**
```json
{
  "weaknessTopics": [
    {
      "topic": "Physics",
      "avgPercentage": 62.5,
      "attemptCount": 4
    },
    {
      "topic": "Chemistry",
      "avgPercentage": 58.3,
      "attemptCount": 3
    }
  ]
}
```

**Response (200 OK - No Data):**
```json
{
  "weaknessTopics": [],
  "message": "No test data available yet"
}
```

---

### GET /student/focus-session/<exam_id>
**Fetch 10 random questions from student's weakest topics for focused drilling**

**Parameters:**
- `exam_id` (path): ID of the exam (e.g., 1 for JEE Main)

**Response (200 OK):**
```json
{
  "focusTopics": ["Physics", "Chemistry"],
  "questions": [
    {
      "questionId": 1,
      "questionText": "A particle moves in a circle. Which is correct?",
      "options": ["Velocity is constant", "Acceleration is zero", "Speed is constant", "Direction is constant"],
      "topic": "Physics",
      "subTopic": "Mechanics"
    }
  ],
  "totalQuestions": 10
}
```

**Response (400 Bad Request):**
```json
{
  "error": "No weakness data available"
}
```

---

### POST /api/log-activity
**Log user activities (login, test start, focus sessions, etc.)**

**Request:**
```json
{
  "activity_type": "FocusSession",
  "duration": 1800,
  "exam_id": 1,
  "assignment_id": null,
  "details": {
    "questions_solved": 10,
    "topic": "Physics"
  }
}
```

**Activity Types:**
- `Login` - User login
- `Logout` - User logout
- `TestStart` - Started a test
- `TestSubmit` - Submitted test answers
- `FocusSession` - Focused study session
- `DoubtsSubmitted` - Submitted doubt
- `ViewedResources` - Viewed learning resources

**Response (201 Created):**
```json
{
  "message": "Activity logged successfully"
}
```

---

### POST /student/submit-doubt
**Submit a doubt/question for teacher resolution**

**Request:**
```json
{
  "topic": "Physics",
  "doubt_text": "I don't understand circular motion concepts",
  "question_id": 5,
  "priority": "High"
}
```

**Priority Levels:** `Low`, `Medium`, `High`

**Response (201 Created):**
```json
{
  "message": "Doubt submitted successfully",
  "doubtId": 42
}
```

---

### GET /api/student/performance
**Get comprehensive performance metrics for visualization**

**Response (200 OK):**
```json
{
  "progression": [
    {
      "date": "2024-11-15",
      "percentage": 75.5
    },
    {
      "date": "2024-11-16",
      "percentage": 82.0
    }
  ],
  "topicBreakdown": [
    {
      "topic": "Physics",
      "percentage": 72.5,
      "testCount": 4
    },
    {
      "topic": "Chemistry",
      "percentage": 68.0,
      "testCount": 3
    }
  ],
  "studyHoursThisWeek": 12.5
}
```

---

## 👨‍🏫 Teacher Portal Endpoints

### GET /teacher/dashboard
**Load teacher main dashboard page**

**Response:** HTML page with embedded JavaScript for data loading

---

### GET /api/teacher/student-roster
**Get all assigned students with engagement scores**

**Response (200 OK):**
```json
{
  "students": [
    {
      "studentId": 1,
      "name": "John Doe",
      "username": "johndoe",
      "engagementScore": 78.5,
      "studyHours": 15.5,
      "completionRate": 85.0,
      "trophyCount": 3,
      "scoreLevel": "High"
    },
    {
      "studentId": 2,
      "name": "Sarah Smith",
      "username": "sarahsmith",
      "engagementScore": 62.3,
      "studyHours": 8.0,
      "completionRate": 60.0,
      "trophyCount": 1,
      "scoreLevel": "Medium"
    }
  ]
}
```

**Score Levels:**
- `High`: ≥ 70
- `Medium`: 40-69
- `Low`: < 40

---

### POST /api/teacher/assignment/create
**Create new assignment(s) for one or more students**

**Request:**
```json
{
  "exam_id": 1,
  "student_ids": [1, 2, 3],
  "due_date": "2024-12-25"
}
```

**Response (201 Created):**
```json
{
  "message": "Assignments created successfully",
  "assignmentIds": [101, 102, 103]
}
```

**Response (400 Bad Request):**
```json
{
  "error": "exam_id and student_ids are required"
}
```

---

### POST /api/teacher/analysis/question-effectiveness
**Analyze question effectiveness: success rates and completion times**

**Request:**
```json
{
  "exam_id": 1
}
```

**Response (200 OK):**
```json
{
  "analysis": [
    {
      "questionId": 1,
      "questionText": "A particle moves in a circle...",
      "topic": "Physics",
      "subTopic": "Mechanics",
      "avgCompletionTime": 45.5,
      "totalAttempts": 12,
      "successRate": 83.33,
      "difficulty": "Low"
    },
    {
      "questionId": 2,
      "questionText": "Which is the IUPAC name...",
      "topic": "Chemistry",
      "subTopic": "Organic",
      "avgCompletionTime": 52.0,
      "totalAttempts": 10,
      "successRate": 40.0,
      "difficulty": "Hard"
    }
  ]
}
```

**Difficulty Classification:**
- `Low`: Success Rate ≥ 70%
- `Medium`: Success Rate 30-70%
- `Hard`: Success Rate < 30%

---

### GET /api/teacher/doubts-frequency
**Get frequency of doubts by topic - creates heatmap data**

**Response (200 OK):**
```json
{
  "doubtsByTopic": [
    {
      "topic": "Physics",
      "count": 15
    },
    {
      "topic": "Chemistry",
      "count": 12
    },
    {
      "topic": "Biology",
      "count": 8
    }
  ]
}
```

---

## 📊 Data Models

### Engagement Score Formula
```
EngagementScore = (StudyHours × 0.3) + (CompletionRate × 0.004) + (TrophyCount × 10)
```

- **StudyHours**: Sum of FocusSession durations (in seconds) divided by 3600
- **CompletionRate**: Percentage of assigned tests completed
- **TrophyCount**: Number of achievements earned

### Success Rate Calculation
```
SuccessRate = (Students who scored ≥50% / Total attempts) × 100
```

### Average Completion Time
```
AvgCompletionTime = SUM(CompletionTime) / COUNT(Attempts) in seconds
```

---

## 🔄 Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource successfully created |
| 302 | Redirect - Redirect to another page |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Not authenticated |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Server Error - Database or server error |

---

## 🔒 Authentication Examples

### Using cURL
```bash
# Register
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@test.com","password":"Pass123!","role":"Student"}'

# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"john","password":"Pass123!"}'

# Use cookies for authenticated requests
curl http://localhost:5000/api/student/performance \
  -b cookies.txt
```

### Using JavaScript Fetch
```javascript
// Login
const loginResponse = await fetch('/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'john', password: 'Pass123!' })
});

// Authenticated request (cookies sent automatically)
const performanceResponse = await fetch('/api/student/performance');
const data = await performanceResponse.json();
```

---

## 🎯 Achievement Criteria

Achievements are automatically awarded based on:

1. **Focused Learner**
   - Criteria: 5+ hours of FocusSession in past 7 days
   - Points: 50

2. **High Scorer**
   - Criteria: Score ≥ 90% on any test
   - Points: 100

3. **Consistent**
   - Criteria: Login on 7 consecutive days
   - Points: 75

4. **Problem Solver**
   - Criteria: Get 5+ doubts cleared
   - Points: 80

---

## ⚙️ Query Parameters

### Pagination (Future Enhancement)
```
GET /api/results?page=1&limit=20
```

### Filtering (Future Enhancement)
```
GET /api/questions?topic=Physics&difficulty=Hard
GET /api/doubts?status=Pending&priority=High
```

### Sorting (Future Enhancement)
```
GET /api/student-roster?sort=engagementScore&order=desc
```

---

## 🔧 Error Handling

**Standard Error Response:**
```json
{
  "error": "Descriptive error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-11-18T10:30:00Z"
}
```

**Common Errors:**
- `INVALID_CREDENTIALS`: Login with wrong username/password
- `DUPLICATE_USER`: Username or email already exists
- `DB_CONNECTION_ERROR`: Database connection failed
- `UNAUTHORIZED`: User not authenticated
- `FORBIDDEN`: User lacks permissions
- `NOT_FOUND`: Resource doesn't exist

---

## 📈 Rate Limiting (Future)
```
Rate Limit: 100 requests per minute per user
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1700325000
```

---

## 📝 Changelog

### Version 1.0.0 (November 18, 2025)
- Initial release
- Core authentication system
- Student and teacher portals
- Weakness topic drilling
- Engagement scoring
- Question effectiveness analysis
- Activity logging
- Gamification system

---

**Last Updated**: November 18, 2025  
**Maintainer**: LearnMatrix Development Team
