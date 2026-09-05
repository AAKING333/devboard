import os
import tempfile

import pytest

from app import create_app
from app.database import init_db


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()

    app.config.update(
        TESTING=True,
        DATABASE=db_path,
    )

    with app.app_context():
        init_db()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()