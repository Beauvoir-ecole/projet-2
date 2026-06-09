"""Shared pytest fixtures.

A throwaway SQLite database is created in-memory so tests never touch
the real Postgres instance.
"""
import pytest

from app import app as flask_app
from models import db


@pytest.fixture
def app():
    """Configure Flask for an isolated test run."""
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        # Drop any pg8000/SSL engine options inherited from a real DATABASE_URL
        # in .env — SQLite must connect without them.
        SQLALCHEMY_ENGINE_OPTIONS={},
        WTF_CSRF_ENABLED=False,
    )
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A Flask test client bound to the in-memory database."""
    return app.test_client()
