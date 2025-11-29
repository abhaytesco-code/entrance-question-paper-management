# Quick Start Testing Guide - Assignment Submission Feature

## Summary of Changes
You now have a complete assignment submission system where:
- **Students** can view pending assignments and upload files
- **Teachers** can view student submissions and grade them with feedback
- All files are securely stored and accessible only to authorized users

## What Was Implemented

### Backend API (Flask)
- ✅ 5 new endpoints for submission handling, viewing, and grading
- ✅ Database table `AssignmentSubmissions` created
- ✅ File upload with validation and secure storage
- ✅ Authorization checks (students see only their assignments, teachers can only grade their own)

### Student UI
- ✅ Enhanced `templates/student/assignments.html` with:
  - Pending Assignments tab (shows assignments to do)
  - Submitted Assignments tab (shows completed + graded work)
  - Drag-and-drop file upload
  - View grades and teacher feedback

### Teacher UI
- ✅ Enhanced `templates/teacher/assignments.html` with:
  - New "View Submissions" tab
  - Grid of assignments with submission counts
  - Submission table for each assignment
  - Grading modal (enter grade 0-100 + feedback)
  - File download capability

### Sample Data
- ✅ 14 assignments created for 12 students across 3 exams
- ✅ Ready to test with different assignment statuses

## How to Test

### Step 1: Verify Database Setup
All components are ready. The database table was created automatically.

### Step 2: Start Flask Application
```powershell
cd "c:\Users\iamab\OneDrive\Desktop\cs prjct"
python app.py
```

Then navigate to: http://127.0.0.1:5000

### Step 3: Test as Student

#### Login as Student
1. Go to http://127.0.0.1:5000/login
2. Login with any student account (created during system setup)
3. Click "Assignments" in sidebar or navigation

#### View Pending Assignments
- Should see list of assignments to complete
- Click first tab: "📝 Pending Assignments"
- Assignments should show with exam names and due dates

#### Upload an Assignment
1. Click on an assignment
2. Either:
   - **Drag and drop** a PDF/DOC file onto the upload area, OR
   - **Click** "Browse" to select file
3. File uploads automatically
4. See success message: "Assignment submitted successfully"
5. File now appears in "📥 Submitted Assignments" tab

#### View Submitted Assignments
1. Click "📥 Submitted Assignments" tab
2. Should see the file you just uploaded
3. Click the filename to download your submission

### Step 4: Test as Teacher

#### Login as Teacher
1. Logout from student account (click profile → Logout)
2. Login with teacher account
3. Click "Assignments" in sidebar or navigation

#### View Student Submissions
1. Should see "📝 Manage Assignments" tab (existing) and "📥 View Submissions" tab (new)
2. Click "📥 View Submissions" tab
3. See grid of exams with submission counts (e.g., "Submitted: 5/12")
4. Click on an exam card

#### Grade a Submission
1. Table appears showing all student submissions
2. Columns: Student Name, Submitted Date, File, Grade, Status
3. Find a submission with "Pending" status
4. Click "Grade" button
5. Modal opens - enter:
   - Grade (e.g., 85)
   - Feedback (e.g., "Great work! Well explained.")
6. Click "Save Grade & Feedback"
7. Success message: "Grade saved successfully!"
8. See grade appears in table as "85/100" with "Graded" status

#### Download Student Work
1. In submissions table, click the filename link
2. File downloads to your computer
3. You can review it before grading

### Step 5: Verify Student Sees Feedback

1. Logout teacher account
2. Login as the student you graded
3. Go to Assignments → "Submitted Assignments" tab
4. Find the assignment you graded
5. **See your grade and teacher feedback!**

## What to Expect

### Expected Behaviors

**Student Dashboard - Pending Assignments Tab**
```
Assignment: JEE Main 2025
Due: 2025-02-15
[Upload file area with drag-drop]
[Browse button]
[Submit button]
```

**Student Dashboard - Submitted Assignments Tab**
```
Assignment: NEET 2025
Submitted: Jan 22, 2025 3:45 PM
File: assignment.pdf [Download]
Grade: 92/100
Feedback: "Excellent submission with clear explanations!"
```

**Teacher Dashboard - View Submissions Tab**
```
[Grid of exams with cards]
JEE Main 2025
- Students: 12
- Completed: 7
- Progress: 58%

[Click card → Opens submission table]
Student Name          | Submitted           | File     | Grade  | Status
John Smith            | Jan 22, 2025 2:30   | work.pdf | 85/100 | Graded
Emma Johnson          | Jan 22, 2025 3:15   | submit.pdf | —    | Pending [Grade]
```

## Troubleshooting

### Issue: "File upload fails"
- **Check**: File type is allowed (PDF, DOC, DOCX, TXT, JPG, PNG, XLS, XLSX, PPT, PPTX)
- **Check**: File size is reasonable (< 50MB)
- **Check**: Browser console for error messages

### Issue: "Can't see other student's submissions"
- **Expected**: Students only see their own submissions
- **Expected**: Students can't access teacher pages
- **This is correct behavior** ✅

### Issue: "Grade button not working"
- **Check**: You're logged in as a teacher
- **Check**: Browser console for JavaScript errors (F12 → Console tab)

### Issue: "File download fails"
- **Check**: You're either the student OR the assignment's teacher
- **Check**: File still exists in `uploads/submissions/` folder
- **Check**: Folder has proper read permissions

## Sample Test Data

**Students**: 12 total (Various names with IDs 100-111)
**Teachers**: 6 total (Various names with IDs 200+)
**Exams**: 3 total
- JEE Main 2025 (ID: 24)
- NEET 2025 (ID: 25)
- CAT 2025 (ID: 26)

**Assignments**: 14 total (3-4 per student with varied statuses)

## File Locations

**Uploaded Files**: `uploads/submissions/{assignment_id}/`
**Example**: `uploads/submissions/1/101_1732000000.pdf`

**Templates**:
- Student: `templates/student/assignments.html`
- Teacher: `templates/teacher/assignments.html`

**API Code**: `app.py` (lines 2347-2650)

## Success Criteria

✅ **Feature is complete when**:
1. Student can upload a file for an assignment
2. File appears in "Submitted Assignments" tab
3. Teacher can see the submission in their View Submissions tab
4. Teacher can download the file
5. Teacher can enter grade and feedback
6. Student sees the grade and feedback
7. Status badges show correctly (Pending/Graded)

## Next Steps

1. **Test** the full workflow above
2. **Report** any issues or unexpected behaviors
3. **Request** any improvements or changes
4. **Deploy** to production once testing is complete

---

**Questions?** Check the error messages in:
- Browser console (F12 → Console)
- Flask terminal output (where you ran `python app.py`)
- Database logs (if applicable)

**Have fun testing!** 🎉
