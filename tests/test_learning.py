from app.database import get_db


def test_learning_page_loads(client):
    response = client.get("/learning")

    assert response.status_code == 200
    assert b"No learning entries yet" in response.data


def test_create_learning_entry(client, app):
    response = client.post(
        "/learning/new",
        data={
            "topic": "Flask Testing",
            "category": "Backend",
            "progress": "60",
            "status": "in_progress",
            "notes": "Learning pytest.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Flask Testing" in response.data
    assert b"Learning entry created successfully." in response.data

    with app.app_context():
        entry = get_db().execute(
            """
            SELECT *
            FROM learning_entries
            WHERE topic = ?
            """,
            ("Flask Testing",),
        ).fetchone()

        assert entry is not None
        assert entry["progress"] == 60
        assert entry["status"] == "in_progress"


def test_learning_rejects_invalid_progress(client, app):
    response = client.post(
        "/learning/new",
        data={
            "topic": "Bad Progress",
            "category": "",
            "progress": "150",
            "status": "in_progress",
            "notes": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Progress must be between 0 and 100." in response.data

    with app.app_context():
        entry = get_db().execute(
            """
            SELECT *
            FROM learning_entries
            WHERE topic = ?
            """,
            ("Bad Progress",),
        ).fetchone()

        assert entry is None