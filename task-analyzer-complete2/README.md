Author: K L MANDARA

🔗 LinkedIn: https://www.linkedin.com/in/klmandara

📧 Email: klmandara@gmail.com

1. Introduction

This project is developed as part of the Software Development Intern Assignment for Singularium Technologies Pvt. Ltd.

The goal is to build a small application that can score, sort, and prioritize tasks based on multiple factors such as urgency, importance, effort, and dependencies.
The project includes:

Django backend

HTML/CSS/JavaScript frontend

Priority scoring algorithm

Additional problem-solving features requested in the assignment

2. How to Run the Project
Backend Setup

Create a virtual environment:

python -m venv venv


Activate it:

Windows

venv\Scripts\activate


Linux/macOS

source venv/bin/activate


Install the required packages:

pip install -r requirements.txt


Run migrations:

cd backend
python manage.py migrate


Start the server:

python manage.py runserver

Frontend

Open:

frontend/index.html


in your web browser.

3. How the Algorithm Works (Summary)

The scoring algorithm considers four main factors:

Urgency

Based on how close the due date is

Overdue tasks get additional weight

Tasks due on weekends or holidays are treated as slightly more urgent

Importance

User-assigned value (1–10)

Higher importance increases the final score

Effort

Tasks with fewer estimated hours gain a “quick win” advantage

Dependencies

Tasks that block other tasks receive a higher score

The algorithm normalizes these values and applies different weight combinations depending on the selected strategy:

Smart Balance

Fastest Wins

High Impact

Deadline Driven

Circular dependencies are automatically detected and highlighted.

A simple learning/feedback system is included to slightly adjust weights when the user marks suggestions as helpful.

4. Design Highlights

Clear separation between scoring logic and API endpoints

Frontend allows task input, bulk JSON input, and switching between strategies

Visual dependency graph using Cytoscape.js

Eisenhower Matrix view for urgency vs. importance

GitHub Actions workflow added for unit test automation

5. Time Spent
Task	Time
Planning & algorithm design	~1 hr 30 min
Backend endpoints	~45 min
Frontend UI	~35 min
Bonus features	~1 hr 15 min
Writing tests	~20 min
Documentation	~20 min
Repo setup + CI	~20 min

Total: approx. 4.5 hours

6. Running Tests
cd backend
python -m unittest

7. Future Improvements

Add authentication and save tasks for each user

Improve UI styling and responsiveness

More detailed feedback learning model

Extend holiday detection with region-specific calendars

8. Project Structure
backend/
    manage.py
    task_analyzer/
    tasks/
frontend/
    index.html
    styles.css
    script.js
docs/
    assignment.pdf
requirements.txt
README.md
