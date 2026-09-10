from app.database import get_db


def test_notes_page_loads(client):
    response = client.get("/notes")

    assert response.status_code == 200
    assert b"No notes yet" in response.data


def test_create_note(client, app):
    response = client.post(
        "/notes/new",
        data={
            "title": "Flask Notes",
            "category": "Backend",
            "content": "Blueprints organize Flask routes.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Flask Notes" in response.data
    assert b"Note created successfully." in response.data

    with app.app_context():
        note = get_db().execute(
            "SELECT * FROM notes WHERE title = ?",
            ("Flask Notes",),
        ).fetchone()

        assert note is not None
        assert note["category"] == "Backend"


def test_create_note_rejects_empty_title(client, app):
    response = client.post(
        "/notes/new",
        data={
            "title": "",
            "category": "",
            "content": "Some content",
        },
        follow_redirects=True,
    )

    assert b"Note title is required." in response.data

    with app.app_context():
        note = get_db().execute(
            "SELECT * FROM notes"
        ).fetchone()

        assert note is None


def test_create_note_rejects_empty_content(client, app):
    response = client.post(
        "/notes/new",
        data={
            "title": "Empty Note",
            "category": "",
            "content": "",
        },
        follow_redirects=True,
    )

    assert b"Note content is required." in response.data

    with app.app_context():
        note = get_db().execute(
            "SELECT * FROM notes WHERE title = ?",
            ("Empty Note",),
        ).fetchone()

        assert note is None