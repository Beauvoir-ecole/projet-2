"""Database connections — SQLAlchemy for Postgres, PyMongo for Mongo Atlas."""
from __future__ import annotations

import os
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient

db = SQLAlchemy()

_mongo_client: Optional[MongoClient] = None


def get_mongo_client() -> MongoClient:
    """Lazy singleton for the Mongo client."""
    global _mongo_client
    if _mongo_client is None:
        url = os.environ.get("MONGO_URL")
        if not url:
            raise RuntimeError("MONGO_URL is not set. See .env.example.")
        _mongo_client = MongoClient(url, serverSelectionTimeoutMS=5000)
    return _mongo_client


def get_mongo_db():
    """Return the application database handle from the Mongo client."""
    name = os.environ.get("MONGO_DB_NAME", "projet_2")
    return get_mongo_client()[name]
