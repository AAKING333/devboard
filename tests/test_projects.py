from app.database import get_db


def test_projects_page_loads(client):
    response = client.get("/projects")

    assert response.status_code == 200
    assert b"No projects yet" in response.data


def test_create_project(client, app):
    response = client.post(
        "/projects/new",
        data={
            "name": "DevBoard",
            "description": "Personal developer dashboard.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"DevBoard" in response.data

    with app.app_context():
        project = get_db().execute(
            """
            SELECT *
            FROM projects
            WHERE name = ?
            """,
            ("DevBoard",),
        ).fetchone()

        assert project is not None
        assert project["status"] == "active"
        
def test_edit_project(client, app):
    with app.app_context():
        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO projects (name, description)
            VALUES (?, ?)
            """,
            ("Old Project", "Old description"),
        )

        db.commit()
        project_id = cursor.lastrowid

    response = client.post(
        f"/projects/{project_id}/edit",
        data={
            "name": "Updated Project",
            "description": "Updated description",
            "status": "paused",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Updated Project" in response.data

    with app.app_context():
        project = get_db().execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()

        assert project["status"] == "paused"


def test_delete_project(client, app):
    with app.app_context():
        db = get_db()

        cursor = db.execute(
            "INSERT INTO projects (name) VALUES (?)",
            ("Delete Project",),
        )

        db.commit()
        project_id = cursor.lastrowid

    response = client.post(
        f"/projects/{project_id}/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        project = get_db().execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()

        assert project is None


def test_missing_project_returns_404(client):
    response = client.get("/projects/999999/edit")

    assert response.status_code == 404
    
def test_dashboard_project_statistics(client, app):
    with app.app_context():
        db = get_db()

        db.execute(
            """
            INSERT INTO projects (name, status)
            VALUES (?, ?)
            """,
            ("Active Project", "active"),
        )

        db.execute(
            """
            INSERT INTO projects (name, status)
            VALUES (?, ?)
            """,
            ("Completed Project", "completed"),
        )

        db.execute(
            """
            INSERT INTO projects (name, status)
            VALUES (?, ?)
            """,
            ("Paused Project", "paused"),
        )

        db.commit()

    response = client.get("/")

    assert response.status_code == 200
    assert b"1 active" in response.data
    assert b"1 completed" in response.data
    assert b"1 paused" in response.data
    assert b"3 total" in response.data
    
def test_create_project_shows_success_message(client):
    response = client.post(
        "/projects/new",
        data={
            "name": "Flash Test Project",
            "description": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Project created successfully." in response.data
    
def test_create_project_rejects_empty_name(client, app):
    response = client.post(
        "/projects/new",
        data={
            "name": "",
            "description": "Invalid project",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Project name is required." in response.data

    with app.app_context():
        project = get_db().execute(
            "SELECT * FROM projects"
        ).fetchone()

        assert project is None


def test_edit_project_rejects_invalid_status(client, app):
    with app.app_context():
        db = get_db()

        cursor = db.execute(
            "INSERT INTO projects (name) VALUES (?)",
            ("Valid Project",),
        )

        db.commit()
        project_id = cursor.lastrowid

    response = client.post(
        f"/projects/{project_id}/edit",
        data={
            "name": "Valid Project",
            "description": "",
            "status": "invalid-status",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid project status." in response.data

    with app.app_context():
        project = get_db().execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()

        assert project["status"] == "active"
        
def test_dashboard_contains_project_chart(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"projectStatusChart" in response.data