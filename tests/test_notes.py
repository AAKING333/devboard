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
        
def test_edit_note(client, app):
    with app.app_context():
        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO notes (title, content)
            VALUES (?, ?)
            """,
            ("Old Note", "Old content"),
        )

        db.commit()
        note_id = cursor.lastrowid

    response = client.post(
        f"/notes/{note_id}/edit",
        data={
            "title": "Updated Note",
            "category": "Flask",
            "content": "Updated content",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Updated Note" in response.data
    assert b"Note updated successfully." in response.data


def test_delete_note(client, app):
    with app.app_context():
        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO notes (title, content)
            VALUES (?, ?)
            """,
            ("Delete Note", "Temporary"),
        )

        db.commit()
        note_id = cursor.lastrowid

    response = client.post(
        f"/notes/{note_id}/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        note = get_db().execute(
            "SELECT * FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()

        assert note is None


def test_missing_note_returns_404(client):
    response = client.get("/notes/999999/edit")

    assert response.status_code == 404


def test_dashboard_note_count(client, app):
    with app.app_context():
        db = get_db()

        db.execute(
            """
            INSERT INTO notes (title, content)
            VALUES (?, ?)
            """,
            ("Note One", "Content"),
        )

        db.execute(
            """
            INSERT INTO notes (title, content)
            VALUES (?, ?)
            """,
            ("Note Two", "Content"),
        )

        db.commit()

    response = client.get("/")

    assert response.status_code == 200
    assert b"2 saved" in response.data