# LearnMatrix - Quick Start Setup Guide

## ⚡ Fast Setup (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database

#### Option A: Windows PowerShell
```powershell
# Start MySQL service
Start-Service MySQL80  # or your MySQL version

# Connect to MySQL
mysql -u root -p

# In MySQL command line, execute:
CREATE DATABASE learnmatrix CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE learnmatrix;
source C:\Users\iamab\OneDrive\Desktop\cs prjct\learnmatrix_schema.sql;
```

#### Option B: Windows Command Prompt
```cmd
# Start MySQL
net start MySQL80

# Execute SQL file
mysql -u root -p learnmatrix < "C:\Users\iamab\OneDrive\Desktop\cs prjct\learnmatrix_schema.sql"
```

### 3. Configure Environment
```bash
# Copy example to .env
copy .env.example .env

# Edit .env with your database credentials
# - DB_USER: your_mysql_username
# - DB_PASSWORD: your_mysql_password
```

### 4. Run Application
```bash
python app.py
```

**Access at**: `http://localhost:5000`

---

## 🔐 Test Credentials

After running the schema setup, the following test users are available:

### Student Account
- **Username**: `student_john`
- **Password**: (Create by registering a new account)
- **Role**: Student

### Teacher Account  
- **Username**: `teacher_admin`
- **Password**: (Create by registering a new account)
- **Role**: Teacher

Or register new accounts via `/register`

---

## 📊 Sample Data Included

The schema script includes sample data:
- **2 Students**: John Doe, Sarah Smith
- **1 Teacher**: Prof Admin
- **3 Exams**: JEE Main, NEET, CAT
- **3 Questions**: Physics, Chemistry, Biology questions

---

## 🐛 Troubleshooting

### Issue: "Can't connect to MySQL server"
```
Solution: 
1. Verify MySQL is running: mysql -u root -p
2. Check DB_HOST, DB_USER, DB_PASSWORD in .env
3. Ensure database 'learnmatrix' exists
```

### Issue: "ModuleNotFoundError: No module named 'flask'"
```
Solution: Reinstall requirements
pip install --upgrade -r requirements.txt
```

### Issue: "Port 5000 already in use"
```
Solution: Kill process or change port in app.py
# Change: app.run(port=5001)
```

### Issue: Session files not persisting
```
Solution: Create 'flask_session' directory in project root
mkdir flask_session
```

---

## 📁 File Structure After Setup

```
cs prjct/
├── app.py                          ✅ Core Flask app
├── config.py                       ✅ Configuration
├── .env                            ✅ (Create from .env.example)
├── requirements.txt                ✅ Dependencies
├── learnmatrix_schema.sql          ✅ Database DDL
├── README.md                       ✅ Full documentation
├── SETUP.md                        ✅ This file
├── flask_session/                  📁 Session storage (auto-created)
├── uploads/                        📁 File uploads (auto-created)
├── templates/
│   ├── base.html                   ✅ Base template
│   ├── login.html                  ✅ Login page
│   ├── register.html               ✅ Registration page
│   ├── student/
│   │   └── dashboard.html          ✅ Student dashboard
│   └── teacher/
│       └── dashboard.html          ✅ Teacher dashboard
└── static/                         📁 (Optional for CSS/JS)
```

---

## 🚀 Next Steps

1. **Login** at `http://localhost:5000/login`
2. **Register** new accounts via `/register`
3. **Student Dashboard**: View analytics and weakness topics
4. **Teacher Dashboard**: Manage students and analyze effectiveness
5. **Explore APIs** via Postman or curl

---

## 📚 Key Routes Reference

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Home/Redirect to dashboard |
| `/login` | GET, POST | User authentication |
| `/register` | GET, POST | New user registration |
| `/logout` | GET | Logout and clear session |
| `/student/dashboard` | GET | Student main portal |
| `/api/student/performance` | GET | Performance data for charts |
| `/api/student/weakness-topics` | GET | Identify weak areas |
| `/student/focus-session/<id>` | GET | Weakness drill questions |
| `/api/log-activity` | POST | Log activities |
| `/student/submit-doubt` | POST | Submit doubts |
| `/teacher/dashboard` | GET | Teacher main portal |
| `/api/teacher/student-roster` | GET | Student engagement scores |
| `/api/teacher/analysis/question-effectiveness` | POST | Question analysis |

---

## 🔧 Customization

### Change Primary Color (Gold to Blue)
Edit `base.html` CSS variables:
```css
:root {
    --accent-gold: #3b82f6;  /* Change primary color */
    --accent-blue: #fbbf24;  /* Swap with secondary */
}
```

### Change Database Name
Edit `.env`:
```env
DB_NAME=my_custom_db_name
```

### Add Your Own Exams
```sql
INSERT INTO Exams (ExamName, Description, TotalQuestions, TotalTime)
VALUES ('Your Exam', 'Description', 100, 180);
```

---

## 📖 API Examples

### Create Assignment
```bash
curl -X POST http://localhost:5000/api/teacher/assignment/create \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": 1,
    "student_ids": [1, 2],
    "due_date": "2024-12-31"
  }'
```

### Log Activity
```bash
curl -X POST http://localhost:5000/api/log-activity \
  -H "Content-Type: application/json" \
  -d '{
    "activity_type": "FocusSession",
    "duration": 1800,
    "exam_id": 1
  }'
```

### Get Student Performance
```bash
curl http://localhost:5000/api/student/performance
```

---

## 🎯 Performance Tips

1. **Add Database Indexes**: Already included in schema
2. **Enable Query Caching**: Implement Redis (future enhancement)
3. **Compress Static Files**: Use gzip in production
4. **Minify CSS/JS**: Use CDN for Chart.js
5. **Use Connection Pooling**: Implement in production config

---

## 🔒 Security Checklist

- [ ] Change `SECRET_KEY` in .env
- [ ] Use strong MySQL password
- [ ] Enable HTTPS in production (SSL certificates)
- [ ] Set `DEBUG=False` in production
- [ ] Use environment-specific `.env` files
- [ ] Implement rate limiting (future)
- [ ] Add CSRF protection (future)
- [ ] Enable 2FA for teachers (future)

---

## 📞 Support Commands

```bash
# Check Flask version
flask --version

# Check Python version
python --version

# Test database connection
python -c "from app import get_db_connection; print(get_db_connection())"

# View all routes
python -c "from app import app; print([str(rule) for rule in app.url_map.iter_rules()])"
```

---

**Last Updated**: November 18, 2025  
**Version**: 1.0.0
