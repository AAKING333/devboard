from app.database import get_db


def test_tasks_page_loads(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert b"No tasks yet" in response.data


def test_create_task(client, app):
    response = client.post(
        "/tasks/new",
        data={
            "title": "Write automated tests",
            "description": "Test DevBoard task creation.",
            "priority": "high",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Write automated tests" in response.data

    with app.app_context():
        task = get_db().execute(
            "SELECT * FROM tasks WHERE title = ?",
            ("Write automated tests",),
        ).fetchone()

        assert task is not None
        assert task["priority"] == "high"


def test_edit_task(client, app):
    with app.app_context():
        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO tasks (title, description, priority)
            VALUES (?, ?, ?)
            """,
            ("Old title", "Old description", "low"),
        )

        db.commit()
        task_id = cursor.lastrowid

    response = client.post(
        f"/tasks/{task_id}/edit",
        data={
            "title": "Updated title",
            "description": "Updated description",
            "priority": "medium",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Updated title" in response.data


def test_complete_task(client, app):
    with app.app_context():
        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO tasks (title)
            VALUES (?)
            """,
            ("Complete me",),
        )

        db.commit()
        task_id = cursor.lastrowid

    response = client.post(
        f"/tasks/{task_id}/complete",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        task = get_db().execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        assert task["status"] == "completed"


def test_delete_task(client, app):
    with app.app_context():
        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO tasks (title)
            VALUES (?)
            """,
            ("Delete me",),
        )

        db.commit()
        task_id = cursor.lastrowid

    response = client.post(
        f"/tasks/{task_id}/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        task = get_db().execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        assert task is None


def test_missing_task_returns_404(client):
    response = client.get("/tasks/999999/edit")

    assert response.status_code == 404
    
    

def test_dashboard_task_statistics(client, app):
    with app.app_context():
        db = get_db()

        db.execute(
            """
            INSERT INTO tasks (title, status)
            VALUES (?, ?)
            """,
            ("Pending task", "pending"),
        )

        db.execute(
            """
            INSERT INTO tasks (title, status)
            VALUES (?, ?)
            """,
            ("Completed task", "completed"),
        )

        db.commit()

    response = client.get("/")

    assert response.status_code == 200

    assert b"1 pending" in response.data
    assert b"1 completed" in response.data
    assert b"2 total" in response.data
    
def test_create_task_with_project(client, app):
    with app.app_context():
        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO projects (name)
            VALUES (?)
            """,
            ("DevBoard",),
        )

        db.commit()
        project_id = cursor.lastrowid

    response = client.post(
        "/tasks/new",
        data={
            "title": "Relational task",
            "description": "Belongs to DevBoard.",
            "priority": "high",
            "project_id": project_id,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"DevBoard" in response.data

    with app.app_context():
        task = get_db().execute(
            """
            SELECT *
            FROM tasks
            WHERE title = ?
            """,
            ("Relational task",),
        ).fetchone()

        assert task["project_id"] == project_id
        
def test_deleting_project_unassigns_task(client, app):
    with app.app_context():
        db = get_db()

        project_cursor = db.execute(
            "INSERT INTO projects (name) VALUES (?)",
            ("Temporary Project",),
        )

        project_id = project_cursor.lastrowid

        task_cursor = db.execute(
            """
            INSERT INTO tasks (title, project_id)
            VALUES (?, ?)
            """,
            ("Keep this task", project_id),
        )

        task_id = task_cursor.lastrowid

        db.commit()

    client.post(
        f"/projects/{project_id}/delete",
        follow_redirects=True,
    )

    with app.app_context():
        task = get_db().execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        assert task is not None
        assert task["project_id"] is None

def test_create_task_shows_success_message(client):
    response = client.post(
        "/tasks/new",
        data={
            "title": "Flash test task",
            "description": "",
            "priority": "medium",
            "project_id": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Task created successfully." in response.data
    
def test_create_task_rejects_empty_title(client, app):
    response = client.post(
        "/tasks/new",
        data={
            "title": "",
            "description": "Invalid task",
            "priority": "medium",
            "project_id": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Task title is required." in response.data

    with app.app_context():
        task = get_db().execute(
            "SELECT * FROM tasks"
        ).fetchone()

        assert task is None


def test_create_task_rejects_invalid_priority(client, app):
    response = client.post(
        "/tasks/new",
        data={
            "title": "Bad priority task",
            "description": "",
            "priority": "extreme",
            "project_id": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid task priority." in response.data

    with app.app_context():
        task = get_db().execute(
            """
            SELECT *
            FROM tasks
            WHERE title = ?
            """,
            ("Bad priority task",),
        ).fetchone()

        assert task is None
        
def test_create_task_rejects_invalid_project(client, app):
    response = client.post(
        "/tasks/new",
        data={
            "title": "Invalid project task",
            "description": "",
            "priority": "medium",
            "project_id": "999999",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Selected project does not exist." in response.data

    with app.app_context():
        task = get_db().execute(
            """
            SELECT *
            FROM tasks
            WHERE title = ?
            """,
            ("Invalid project task",),
        ).fetchone()

        assert task is None
        
def test_dashboard_contains_task_chart_data(client, app):
    with app.app_context():
        db = get_db()

        db.execute(
            """
            INSERT INTO tasks (title, status)
            VALUES (?, ?)
            """,
            ("Pending Chart Task", "pending"),
        )

        db.execute(
            """
            INSERT INTO tasks (title, status)
            VALUES (?, ?)
            """,
            ("Completed Chart Task", "completed"),
        )

        db.commit()

    response = client.get("/")

    assert response.status_code == 200
    assert b"taskStatusChart" in response.data
    assert b"Pending" in response.data
    assert b"Completed" in response.data