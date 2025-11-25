# Smart Task Analyzer (recreated)

## Continuous Integration
This repository includes a GitHub Actions workflow (`.github/workflows/python-tests.yml`) that installs dependencies and runs the unit tests on push and pull requests. The workflow runs tests located under `backend/tasks/tests.py`.

## Bonus features implemented
- Dependency graph visualization (frontend): a simple SVG renderer available via **Show Dependency Graph** button in the UI.
- Weekend-aware urgency: the scoring algorithm computes business days until due date (excludes weekends) and supports an optional `backend/tasks/holidays.json` for custom holiday dates.



## Bonus Features Implemented
- **Dependency Graph Visualization:** Frontend includes a Cytoscape.js-based dependency graph under "Dependency Graph". It visualizes tasks and edges from dependency -> dependent.
- **Date Intelligence (Weekends/Holidays):** The scoring algorithm treats due dates falling on weekends or listed holidays as slightly more urgent.
- **Eisenhower Matrix View:** The frontend renders tasks into the 2x2 Eisenhower matrix (Urgent/Important).
- **Learning System (Feedback):** A feedback endpoint (`POST /api/tasks/feedback/`) lets users submit small adjustments to the strategy weights. These are saved in `backend/tasks/scoring_config.json` and used on subsequent analyzes.

## Continuous Integration
- A GitHub Actions workflow (`.github/workflows/ci.yml`) runs `pip install -r requirements.txt`, migrations, and the unit tests on push/pull-request to `main`/`master`.
