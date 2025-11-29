# LearnMatrix - Quick Start & Testing Guide

## Server Status ✅
- **Web App:** http://127.0.0.1:5000
- **Status:** Running (Flask development server)
- **Database:** MySQL 8.0 connected
- **Test Data:** Seeded (6 teachers, 12 students)

---

## Test Accounts

### Teacher Accounts (All use password: `test123`)
| Username | Full Name | Email |
|----------|-----------|-------|
| teacher_test | Teacher Test | teacher_test@learnmatrix.edu |
| prof_sharma | Rajesh Sharma | rajesh@learnmatrix.edu |
| dr_patel | Priya Patel | priya@learnmatrix.edu |
| mrs_gupta | Neha Gupta | neha@learnmatrix.edu |
| mr_verma | Anil Verma | anil@learnmatrix.edu |
| dr_singh | Karan Singh | karan@learnmatrix.edu |

### Student Accounts (All use password: `test123`)
| Username | Full Name |
|----------|-----------|
| demo_student | Student Test |
| akshay_sharma | Akshay Sharma |
| priya_verma | Priya Verma |
| rahul_patel | Rahul Patel |
| neha_singh | Neha Singh |
| arjun_kumar | Arjun Kumar |
| deepika_gupta | Deepika Gupta |
| rohan_desai | Rohan Desai |
| anjali_nair | Anjali Nair |
| vikram_reddy | Vikram Reddy |
| shreya_iyer | Shreya Iyer |
| aditya_bhat | Aditya Bhat |

---

## How to Login

1. Open http://127.0.0.1:5000/login
2. **For Teacher Testing:**
   - Username: `teacher_test`
   - Password: `test123`
3. **For Student Testing:**
   - Username: `demo_student`
   - Password: `test123`
4. Click **Login**

---

## Testing Features - Teacher Dashboard

### 1. **Teacher Dashboard** (`/teacher/dashboard`)
After login, you'll see:
- ✅ **Total Students Managed** - Shows number of students assigned
- ✅ **Total Study Hours** - Sum of all student focus session durations
- ✅ **Completion Rate** - Percentage of completed assignments
- ✅ **Pending Doubts** - Number of unresolved student doubts

### 2. **All Students** (`/teacher/student-performance`)
View comprehensive student metrics:
- Student names and usernames
- Study hours per student
- Average test scores
- Completed assignments count
- Achievements earned
- Performance level (High/Good/Average/Below Average)
- Join date

### 3. **Analytics** (`/teacher/analytics`)
View class-wide metrics:
- Performance distribution (score ranges: 80-100%, 60-80%, etc.)
- Top 5 performing students
- Assignment completion trend over time

### 4. **Students** (`/teacher/students`)
Manage student roster:
- List of assigned students
- Quick sort/filter options

### 5. **Assignments** (`/teacher/assignments`)
Create and manage assignments:
- Create simple assignments with descriptions
- View completion rates
- Track assignment deadlines

### 6. **Doubts** (`/teacher/doubts`)
Resolve student questions:
- View all pending doubts from students
- See attached images with doubts
- Provide resolution text
- Mark doubts as resolved

### 7. **Resources** (`/teacher/resources`)
Share learning materials

---

## Testing Features - Student Dashboard

### 1. **Student Dashboard** (`/student/dashboard`)
After login, you'll see:
- ✅ **Total Study Time** - Hours spent on platform
- ✅ **Average Test Score** - Overall performance percentage
- ✅ **Achievements** - Trophies earned
- ✅ **Assignments** - Assigned and completed work

### 2. **Assignments** (`/student/assignments`)
View assigned work:
- List of assignments
- Due dates
- Status (Pending/Completed)
- Current scores if available

### 3. **Focus Sessions** (`/student/focus-session`)
Practice with targeted drills:
- Select exam to practice
- Get questions from weak topics
- Submit answers
- Get instant feedback

### 4. **Doubts** (`/student/doubts`)
Submit questions to teachers:
- Write doubt description
- Upload screenshot/image if needed
- Track resolution status
- See teacher's resolution text

### 5. **Achievements** (`/student/achievements`)
View earned badges:
- Trophy names
- Description
- Points
- Date earned

### 6. **Analytics** (`/student/analytics`)
Track your performance:
- Test score progression
- Topic-wise performance
- Activity breakdown (focus sessions, etc.)
- Study hours this week

---

## Quick Testing Checklist

### ✓ Verify Teacher Features
- [ ] Login as `teacher_test`
- [ ] Check dashboard shows stats (total students, study hours, etc.)
- [ ] Navigate to "All Students" - should show student list
- [ ] Go to "Analytics" - should display charts/metrics
- [ ] Check "Doubts" - should list student questions
- [ ] Try creating an assignment
- [ ] View student performance metrics

### ✓ Verify Student Features
- [ ] Login as `demo_student`
- [ ] Check dashboard shows study time and scores
- [ ] View assignments - should show assigned work
- [ ] Check doubts - should show submitted questions
- [ ] View achievements - should show earned badges
- [ ] Check analytics - should show performance charts
- [ ] Try submitting a doubt with an image

### ✓ Verify Database
- [ ] Open http://127.0.0.1:5000/api/db-health in browser
- [ ] Should show: `{"status":"ok","db":"reachable"}`

---

## API Endpoints Reference

### Health Check
```
GET /api/db-health
→ Returns: {"status": "ok", "db": "reachable"}
```

### Student APIs
```
GET /api/student/stats
GET /api/student/assignments
GET /api/student/achievements
GET /api/student/analytics
GET /api/student/weakness-topics
GET /api/student/doubts
GET /api/student/class-stats
GET /api/student/performance
```

### Teacher APIs
```
GET /api/teacher/stats
GET /api/teacher/all-students
GET /api/teacher/student-roster
GET /api/teacher/class-analytics
GET /api/teacher/assignments
GET /api/admin/teachers
GET /api/teacher/doubts
GET /api/teacher/doubts-frequency
POST /api/teacher/assignment/create
POST /api/teacher/respond-doubt
```

### Common APIs
```
POST /api/log-activity
POST /student/submit-doubt
POST /api/teacher/assignment/create-simple
```

---

## Testing Script

Run automated endpoint tests:
```bash
cd "c:\Users\iamab\OneDrive\Desktop\cs prjct"
python test_endpoints.py
```

This will verify:
- Database connectivity
- Student endpoint responses
- Teacher endpoint responses
- Data consistency

---

## Server Control

### Start Server
```bash
cd "c:\Users\iamab\OneDrive\Desktop\cs prjct"
python app.py
```

### Re-seed Database (if needed)
```bash
cd "c:\Users\iamab\OneDrive\Desktop\cs prjct"
python seed_db.py
```

---

## Troubleshooting

### Issue: "Database connection failed"
**Solution:** Ensure MySQL is running
```bash
# Check if MySQL is running
tasklist | findstr mysqld

# If not, start MySQL:
net start MySQL80
```

### Issue: "Login page won't load"
**Solution:** Ensure Flask server is running
```bash
# Check if Flask is running on 5000
netstat -ano | findstr :5000

# If not, restart:
cd "c:\Users\iamab\OneDrive\Desktop\cs prjct"
python app.py
```

### Issue: "API returns 500 error"
**Solution:** Check Flask server console for error messages. May need to:
1. Verify DB connection: http://127.0.0.1:5000/api/db-health
2. Reseed database: `python seed_db.py`
3. Restart Flask server: `python app.py`

---

## Key Fixes Applied Today

✅ Fixed duplicate API route handlers (removed duplicates)
✅ Added missing `/api/admin/teachers` endpoint
✅ Added `/api/db-health` for quick diagnostics
✅ Fixed database numeric type handling (Decimal → float)
✅ Seeded database with realistic test data
✅ All endpoints verified working
✅ Frontend templates aligned with backend APIs

---

## Support

All test data is pre-configured. If you need to:
- **Reset test data:** Run `python seed_db.py`
- **Check API status:** Visit `/api/db-health`
- **Review logs:** Check Flask server console output

---

**Happy Testing!** 🚀
