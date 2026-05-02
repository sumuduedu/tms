# 🎓 Training Management System (TMS)

A comprehensive **Training Management System (TMS)** built with Django, designed to manage the full lifecycle of vocational and academic training — from enrollment to certification and alumni job placement.

---

## 🚀 Project Overview

This system supports:

* Multi-role user management
* Course and module management
* Enrollment workflows
* Batch and teacher assignment
* Lesson planning and timetables
* Learning Management System (LMS)
* Assessment and results tracking
* Certification generation
* NCS/NVQ competency tracking
* Alumni and job portal

---

## 🧱 System Architecture

The system follows **Clean Architecture principles**:

* 🔹 Models → Data layer
* 🔹 Selectors → Query layer
* 🔹 Services → Business logic
* 🔹 Views → Request handling (thin)
* 🔹 Templates → UI layer

---

## 👥 User Roles

* Admin
* Staff
* Teacher
* Student
* Parent
* Alumni

---

## 📦 Features by Phase

---

### 🔹 Phase 1 — Authentication System

* Custom User model (email-based login)
* Role-based access
* Login / Logout
* Dashboard redirection

---

### 🔹 Phase 2 — Course Management

* Create and manage courses
* Module structure (A–K style)
* Publish/unpublish courses
* Public course listing

---

### 🔹 Phase 3 — Enrollment System

* Student/Parent course application
* Enrollment request workflow
* Admin approval/rejection
* Automatic enrollment creation

---

### 🔹 Phase 4 — Batch Management

* Create batches per course
* Assign teachers
* Assign enrolled students
* Batch lifecycle management

---

### 🔹 Phase 5 — Planning System

* Timetable scheduling
* Lesson plan creation
* Teaching structure
* Session management

---

### 🔹 Phase 6 — LMS (Learning Management System)

* Content upload (file, video, link, text)
* Activity creation (assignment, quiz, practice)
* Student submissions
* Teacher evaluation

---

### 🔹 Phase 7 — Assessment & Results

* Attendance tracking
* Assessment creation
* Marks entry
* Final result calculation (Pass/Fail)

---

### 🔹 Phase 8 — Certification System

* Certificate generation
* Unique certificate IDs
* PDF support (optional)
* Download certificates

---

### 🔹 Phase 9 — NCS / NVQ Competency System

* NCS unit management
* Competency tracking
* Task-based assessment
* Student competency progress

---

### 🔹 Phase 10 — Alumni & Job Portal

* Alumni profile creation
* Job posting system
* Industry connection
* Career tracking

---

## 🛠️ Tech Stack

* Python
* Django
* SQLite (development)
* HTML / CSS (Tailwind optional)
* Git & GitHub

---

## 🗂️ Project Structure

```bash
apps/
├── accounts/
├── courses/
├── enrollment/
├── batch/
├── planning/
├── lms/
├── assessment/
├── certification/
├── competency/
├── alumni/
├── core/
│   ├── services/
│   ├── selectors/
│   ├── decorators.py
│   ├── mixins.py
│   └── templatetags/
```

---

## ⚙️ Installation

```bash
git clone <your-repo>
cd tms
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## 🔐 Default Workflow

```text
Student → Apply → Approval → Enrollment → Batch → Learning → Assessment → Certification → Alumni → Jobs
```

---

## 🧠 Design Principles

* DRY (Don’t Repeat Yourself)
* Separation of Concerns
* Clean Architecture
* Role-Based Access Control

---

## 🚀 Future Enhancements

* Machine Learning for student performance prediction
* Analytics dashboard
* API integration (DRF)
* Mobile app support

---

## 👨‍💻 Author

Developed as a **full-stack academic and vocational training system** integrating real-world educational workflows.

---

## 📄 License

This project is for educational and research purposes.
