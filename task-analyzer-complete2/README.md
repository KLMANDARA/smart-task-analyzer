Author: K L MANDARA

🔗 LinkedIn: https://www.linkedin.com/in/klmandara

📧 Email: klmandara@gmail.com

Smart Task Analyzer
1. Setup Instructions
Backend (Django)
python -m venv venv


Activate the environment:

Windows

venv\Scripts\activate


macOS/Linux

source venv/bin/activate


Install dependencies:

pip install -r requirements.txt


Run migrations:

cd backend
python manage.py migrate


Start server:

python manage.py runserver

Frontend

Open:

frontend/index.html

2. Algorithm Explanation (300–500 words)

The Smart Task Analyzer generates a priority score for each task by considering urgency, importance, effort, and dependencies. These factors help identify which tasks are more critical and should be completed earlier.

Urgency is determined from the task’s due date. Tasks closer to the deadline receive higher urgency, and tasks already overdue receive an additional boost. Deadlines falling on weekends or predefined holidays are treated as slightly more urgent since these days often limit available working hours.

Importance uses the user-provided rating on a scale of 1–10. Higher values indicate tasks that should have a stronger influence on the final ranking.

Effort is based on estimated hours. Tasks that require fewer hours contribute more to the final score. This highlights “quick wins,” which can be helpful for productivity and workload balancing.

Dependencies reflect whether a task blocks other tasks. A task with many dependents becomes more valuable to complete early, since it unlocks progress in multiple areas.

All values are normalized so the score is not dominated by any single factor.
After normalization, weights are applied depending on the selected strategy:

Smart Balance: gives similar importance to urgency and importance while still considering effort and dependencies.

Fastest Wins: emphasizes low-effort tasks.

High Impact: heavily prioritizes importance.

Deadline Driven: gives urgency the highest weight.

Circular dependencies are detected using depth-first search. When detected, the system flags the tasks for review.

Overall, the scoring approach aims to balance short-term deadlines, long-term important work, quick wins, and dependency complexity.

3. Design Decisions

Kept scoring logic independent from API endpoints for clarity and testing

Used JSON fields for flexible dependency storage

Added normalization to keep scores consistent

Introduced multiple scoring strategies for different working styles

Included cycle detection for safety

Added minimal validation to prevent incorrect inputs

4. Time Breakdown
Task	Time
Algorithm design	~1 hr 30 min
Backend API	~45 min
Frontend UI	~35 min
Bonus features	~1 hr 15 min
Testing	~20 min
Documentation	~20 min
Repo setup	~20 min
5. Bonus Features Attempted

Dependency graph visualization

Weekend/holiday urgency adjustment

Eisenhower Matrix view

Weight adjustment (learning system)

GitHub Actions automated testing

6. Future Improvements

Improve UI layout and visual design

Add login system and persistent task storage

Provide more advanced weight-tuning

Add automatic holiday calendar

Add user-specific prioritization modes
