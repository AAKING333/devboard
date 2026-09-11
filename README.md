# DevBoard

DevBoard is a personal developer dashboard built with Flask that helps developers organize projects, manage tasks, track learning progress, and maintain technical notes from a single interface.

## Features

### Dashboard

- Overview of tasks, projects, learning progress, and notes
- Task status visualization
- Project status visualization
- Learning progress visualization
- Database-driven statistics using Chart.js

### Task Management

- Create, view, edit, complete, and delete tasks
- Set task priorities
- Associate tasks with projects
- Track pending and completed tasks

### Project Management

- Create, edit, and delete projects
- Track active, paused, and completed projects
- Associate multiple tasks with a project
- Preserve tasks when their associated project is deleted

### Learning Tracker

- Record learning topics
- Organize topics by category
- Track progress from 0% to 100%
- Track not-started, in-progress, and completed learning entries
- Add notes to learning entries

### Notes

- Create and organize development notes
- Categorize notes
- Edit and delete saved notes
- Track creation and update timestamps

## Tech Stack

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Jinja
- Chart.js
- pytest
- Git and GitHub

## Architecture

DevBoard uses a lightweight Flask application structure.

```text
Browser
   |
   v
Flask Routes
   |
   +---- Jinja Templates
   |
   v
SQLite Database
```

Flask handles application logic and HTTP requests, SQLite provides persistent storage, Jinja renders server-side templates, and Chart.js visualizes dashboard statistics in the browser.

## Project Structure

```text
devboard/
|
|-- app/
|   |-- static/
|   |   |-- css/
|   |   `-- js/
|   |
|   |-- templates/
|   |
|   |-- __init__.py
|   |-- database.py
|   |-- routes.py
|   `-- schema.sql
|
|-- tests/
|
|-- .env.example
|-- .gitignore
|-- README.md
|-- requirements.txt
`-- run.py
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/AAKING333/devboard.git
cd devboard
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the database

```bash
flask --app run init_db
```

### 5. Run DevBoard

```bash
python run.py
```

Open the local address displayed by Flask in your browser.

## Testing

DevBoard includes automated tests for its major application behavior.

Run the complete test suite with:

```bash
python -m pytest
```

The tests cover areas including:

- Task management
- Project management
- Learning tracker
- Notes management
- Form validation
- Dashboard statistics
- Dashboard chart integration
- Error handling
- Application configuration

## Database

DevBoard uses SQLite with relational data between projects and tasks.

A task may optionally belong to a project. If a project is deleted, its tasks are preserved and become unassigned rather than being deleted.

Database-level constraints are also used where appropriate, including validation of learning progress and learning status.

## Development Workflow

Development followed a feature-branch Git workflow.

Examples of feature branches used during development include:

```text
feat/project-management
feat/form-feedback
feat/learning-tracker
feat/notes
feat/dashboard-charts
feat/app-polish
```

Changes were developed in logical commits, tested locally, pushed to GitHub, and integrated through pull requests.

## Security and Validation

The application includes:

- Server-side form validation
- Parameterized SQLite queries
- POST requests for destructive operations
- Foreign-key enforcement
- Environment-based secret-key configuration
- Custom error handling

DevBoard is currently intended as a learning and portfolio project rather than a production-ready multi-user service.

## What I Learned

Building DevBoard provided practical experience with:

- Structuring a Flask application
- Designing relational SQLite schemas
- Implementing CRUD operations
- Connecting related database entities
- Server-side validation
- Testing Flask applications with pytest
- Passing backend data into frontend visualizations
- Managing application configuration
- Working with Git feature branches
- Writing meaningful commits
- Using pull requests to integrate features

## Future Improvements

Possible future improvements include:

- User authentication
- CSRF protection
- Search and filtering
- Task due dates
- Improved responsive design
- Database migrations
- REST API support
- Production deployment configuration

## License

This project is currently provided for educational and portfolio purposes.