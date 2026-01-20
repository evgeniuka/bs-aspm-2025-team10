# 🏋️ FitCoach Pro

![Status](https://img.shields.io/badge/Status-Active-success)
![Version](https://img.shields.io/badge/v1.0-blue)

**FitCoach Pro** is a personal training management system designed specifically for **Small Group Training**. It enables trainers to manage 2–4 clients simultaneously in real-time without losing focus on individual coaching.

---

## 🚀 Key Features

* **⚡ Real-Time Split-Screen:** A synchronized 2×2 grid display that updates instantly via WebSockets, allowing trainers to track multiple clients at once.
* **📝 Program Builder:** Create personalized workout plans using a built-in exercise library.
* **👥 Role-Based Access:** Dedicated portals for **Trainers** (management & controls) and **Trainees** (progress view).
* **📊 Analytics:** Automatic data logging and progress visualization for weights, volume, and consistency.

---

## 🛠 Tech Stack

* **Backend:** Python, Flask, Flask-SocketIO, PostgreSQL, SQLAlchemy.
* **Frontend:** React, Vite, Tailwind CSS, Socket.io-client.


## 🧪 Testing
Run the full test suite (including the new Feature 7 session logic):

Bash
cd backend
pytest
Team: Group 10 (BS-ASPM-2025)

---

##Jira
https://sce-ac.atlassian.net/jira/software/projects/ASPM25T10/boards/2205?atlOrigin=eyJpIjoiMjIzZjlmNGRhYWZmNDllZDgwNzllMGNmNzQ0M2JmODAiLCJwIjoiaiJ9


---


## ⚙️ Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
flask run
Frontend
Bash
cd frontend
npm install
npm run dev
---
