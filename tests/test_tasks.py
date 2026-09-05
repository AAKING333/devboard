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