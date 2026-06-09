"""Data layer — SQLAlchemy models (Postgres) and PyMongo repositories (Mongo).

All persistence classes follow the same shape:
  - A plain data class describing the entity.
  - A repository class exposing CRUD operations.
This separation keeps controllers thin and lets the test suite swap
implementations easily.
"""
from .db import db, get_mongo_db
from .category import Category, CategoryRepository
from .service import Service, ServiceRepository
from .testimonial import Testimonial, TestimonialRepository

__all__ = [
    "db",
    "get_mongo_db",
    "Category",
    "CategoryRepository",
    "Service",
    "ServiceRepository",
    "Testimonial",
    "TestimonialRepository",
]
