# Assignment Upload Error - Troubleshooting Guide

## Quick Diagnostic Steps

Follow these steps to identify the upload issue:

### Step 1: Check Browser Console
1. Open your browser (Chrome/Firefox/Edge)
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Try uploading a file again
5. Look for error messages in red
6. **Share the error message** with me

### Step 2: Check Flask Console
1. Look at the terminal where you ran `python app.py`
2. After trying to upload, check for error messages
3. **Share any error messages** with me

### Step 3: Verify Your Setup
Run this command in PowerShell:
```powershell
cd "c:\Users\iamab\OneDrive\Desktop\cs prjct"
python verify_feature.py
```
All checks should pass [OK]

---

## Common Issues & Fixes

### Issue 1: "File type not allowed"
**Cause**: File extension not in allowed list
**Fix**: Use only: PDF, DOC, DOCX, TXT, JPG, JPEG, PNG, XLS, XLSX, PPT, PPTX
**Solution**: Rename your file to one of these extensions

### Issue 2: "Select a file first"
**Cause**: No file selected before clicking Submit
**Fix**: Click "Choose file" button to select a file first

### Issue 3: "Assignment not found or does not belong to you"
**Cause**: Student-assignment mismatch in database
**Fix**: This shouldn't happen if you're logged in as the right student
**Check**: Make sure you're logged in as a student account

### Issue 4: "Database connection failed"
**Cause**: Flask can't connect to MySQL database
**Fix**: 
1. Make sure MySQL is running
2. Check .env file has correct DB_HOST, DB_USER, DB_PASSWORD
3. Verify database name is "learnmatrix"

### Issue 5: Upload appears to work but file doesn't appear in "Submitted" tab
**Cause**: Submitted assignments not loading
**Check**: Press F12 → Console → look for errors when page loads

### Issue 6: Error in Flask console like "cursor not defined"
**Cause**: Database connection error
**Fix**: Restart Flask and check MySQL connection

---

## Complete Diagnostic Check

Open PowerShell and run these commands:

```powershell
# 1. Navigate to project
cd "c:\Users\iamab\OneDrive\Desktop\cs prjct"

# 2. Check database connection
python -c "
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'learnmatrix')
    )
    cursor = conn.cursor()
    
    # Check if student has assignments
    cursor.execute('SELECT UserID, FirstName FROM Users WHERE Role = \"Student\" LIMIT 1')
    user = cursor.fetchone()
    if user:
        student_id = user[0]
        cursor.execute('SELECT COUNT(*) FROM Assignments WHERE StudentID = %s', (student_id,))
        count = cursor.fetchone()[0]
        print(f'SUCCESS: DB connected. Student ID {student_id} has {count} assignments')
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f'ERROR: {e}')
"

# 3. Check uploads directory
if (Test-Path "uploads\submissions") { echo "OK: uploads\submissions exists" } else { echo "MISSING: uploads\submissions" }

# 4. Check API endpoint
curl -X GET http://127.0.0.1:5000/api/student/assignments -Headers @{"Cookie"="your_session_cookie"}
```

---

## What I've Fixed

I identified and fixed an issue in the API endpoint. The fix:
- **Changed**: Assignment endpoint was returning wrong ExamID
- **Fixed**: Now returns correct ExamID from database
- **Result**: Better data consistency

**Action needed**: Restart Flask for the fix to take effect
```powershell
# Stop Flask (Ctrl+C in terminal where it's running)
# Then restart:
python app.py
```

---

## Information I Need From You

Please provide:

1. **Error Message**: What exactly does the error say?
2. **Browser Console**: Any red errors? (F12 → Console)
3. **Flask Console**: Any errors in terminal output?
4. **File Type**: What type of file are you trying to upload? (PDF, DOC, etc.)
5. **Student Account**: Are you logged in as a student?
6. **Assignment Visible**: Can you see the assignment in the Pending tab?

---

## Step-by-Step Debugging

### Test 1: Can you see pending assignments?
1. Login as student
2. Go to Assignments page
3. Click "Pending Assignments" tab
4. Do you see any assignments listed?

**If NO**: Assignment data not loading
**If YES**: Continue to Test 2

### Test 2: Can you select a file?
1. In a pending assignment card
2. Click "Choose file" button
3. Select any PDF or DOC file from your computer
4. Does file name appear?

**If NO**: File picker not working
**If YES**: Continue to Test 3

### Test 3: Does upload button click?
1. With file selected, click "🚀 Submit" button
2. Button should change to "📤 Uploading..."
3. Does it change?

**If NO**: JavaScript issue
**If YES**: Continue to Test 4

### Test 4: Check console for errors
1. Press F12 (Developer Tools)
2. Go to Console tab
3. Try uploading again
4. Any error messages in red?

**Report what you see**

---

## Testing the API Directly (Advanced)

To test if the API works, open PowerShell and run:

```powershell
# Get a valid session cookie first, then test:
$uri = "http://127.0.0.1:5000/api/submit-assignment"
$form = @{
    assignment_id = "1"
    file = Get-Item "C:\path\to\your\file.pdf"
}

# This would require proper authentication and file handling
# Easier: Just use the UI and check browser console for details
```

---

## Next Steps

1. **Provide Error Message**: Tell me what error you see
2. **Run Tests**: Follow the step-by-step debugging above
3. **Share Results**: Let me know what happens at each step
4. **I'll Help**: Based on your info, I can fix the issue

---

## Quick Restart

If nothing works, try a clean restart:

```powershell
# 1. Stop Flask (Ctrl+C in the terminal where it runs)
# 2. Close browser completely
# 3. Reopen browser
# 4. Restart Flask:
cd "c:\Users\iamab\OneDrive\Desktop\cs prjct"
python app.py
# 5. Visit http://127.0.0.1:5000
# 6. Login again
# 7. Try upload
```

---

**Please share the error message and let me know what step you're stuck on!**
