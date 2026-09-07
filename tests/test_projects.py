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