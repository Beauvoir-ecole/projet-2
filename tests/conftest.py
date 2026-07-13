"""Shared pytest fixtures.

A throwaway SQLite database is created in-memory so tests never touch
the real Postgres instance.
"""
import pytest
from sqlalchemy import event

from app import app as flask_app
from models import db


def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
    """SQLite ignore les clés étrangères par défaut : on les active à chaque
    connexion pour que les contraintes FK / cascades soient réellement testées."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


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
        if not event.contains(db.engine, "connect", _enable_sqlite_foreign_keys):
            event.listen(db.engine, "connect", _enable_sqlite_foreign_keys)
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A Flask test client bound to the in-memory database."""
    return app.test_client()
