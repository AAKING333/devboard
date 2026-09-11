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
            "status": "in progress",
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
        assert entry["status"] == "in progress"


def test_learning_rejects_invalid_progress(client, app):
    response = client.post(
        "/learning/new",
        data={
            "topic": "Bad Progress",
            "category": "",
            "progress": "150",
            "status": "in progress",
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
        
def test_edit_learning_entry(client, app):
    # First create an entry to edit
    with app.app_context():
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO learning_entries (topic, category, progress, status, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("Old Topic", "Testing", 10, "in progress", "Initial notes"),
        )
        db.commit()
        entry_id = cursor.lastrowid

    # Send POST request to edit the entry
    response = client.post(
        f"/learning/{entry_id}/edit",
        data={
            "topic": "Updated Topic",
            "category": "Testing",
            "progress": "100",
            "status": "completed",
            "notes": "Updated notes",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Updated Topic" in response.data
    assert b"Learning entry updated successfully." in response.data

    # Verify database update
    with app.app_context():
        entry = get_db().execute(
            "SELECT * FROM learning_entries WHERE id = ?",
            (entry_id,),
        ).fetchone()

    assert entry["topic"] == "Updated Topic"
    assert entry["progress"] == 100
    assert entry["status"] == "completed"


def test_delete_learning_entry(client, app):
    # First create an entry to delete
    with app.app_context():
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO learning_entries (topic, category, progress, status, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("Delete Me", "Testing", 0, "not started", "Temp"),
        )
        db.commit()
        entry_id = cursor.lastrowid

    # Post to delete route
    response = client.post(
        f"/learning/{entry_id}/delete",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Learning entry deleted successfully." in response.data

    # Verify it is removed from the database
    with app.app_context():
        entry = get_db().execute(
            "SELECT * FROM learning_entries WHERE id = ?",
            (entry_id,),
        ).fetchone()

    assert entry is None


def test_learning_entry_404(client):
    # Try editing a non-existent entry ID
    response = client.get("/learning/99999/edit")
    assert response.status_code == 404

    # Try posting to edit a non-existent entry ID
    response = client.post(
        "/learning/99999/edit",
        data={
            "topic": "Ghost",
            "category": "",
            "progress": "50",
            "status": "in progress",
            "notes": "",
        },
    )
    assert response.status_code == 404

    # Try deleting a non-existent entry ID
    response = client.post("/learning/99999/delete")
    assert response.status_code == 404


def test_learning_rejects_completed_without_full_progress(client):
    response = client.post(
        "/learning/new",
        data={
            "topic": "Incomplete Completion",
            "category": "Testing",
            "progress": "90",
            "status": "completed",
            "notes": "",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Completed entries must have 100% progress." in response.data
    
def test_dashboard_learning_statistics(client, app):
    with app.app_context():
        db = get_db()

        db.execute(
            """
            INSERT INTO learning_entries
            (topic, progress, status)
            VALUES (?, ?, ?)
            """,
            ("Flask", 50, "in progress"),
        )

        db.execute(
            """
            INSERT INTO learning_entries
            (topic, progress, status)
            VALUES (?, ?, ?)
            """,
            ("Git", 100, "completed"),
        )

        db.commit()

    response = client.get("/")

    assert response.status_code == 200
    assert b"1 in progress" in response.data
    assert b"1 completed" in response.data
    assert b"2 total" in response.data
    assert b"75% average progress" in response.data
    
def test_dashboard_contains_learning_chart(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"learningProgressChart" in response.data