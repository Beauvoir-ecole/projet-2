"""Populate the Postgres database with fictional categories and services.

Run with:
    python seed/seed_postgres.py

This script is meant to be edited freely — change the lists below to
match your project, or ask Claude / ChatGPT to rewrite them.
"""
import sys
from pathlib import Path

# Allow running this file directly from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app
from models import Category, Service, db


CATEGORIES = [
    {"name": "Catégorie A", "slug": "categorie-a"},
    {"name": "Catégorie B", "slug": "categorie-b"},
    {"name": "Catégorie C", "slug": "categorie-c"},
]

SERVICES = [
    {
        "title": "Service un",
        "description": (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Sed do eiusmod tempor incididunt ut labore et dolore magna."
        ),
        "category_slug": "categorie-a",
        "is_published": True,
    },
    {
        "title": "Service deux",
        "description": (
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco "
            "laboris nisi ut aliquip ex ea commodo consequat."
        ),
        "category_slug": "categorie-a",
        "is_published": True,
    },
    {
        "title": "Service trois",
        "description": (
            "Duis aute irure dolor in reprehenderit in voluptate velit esse "
            "cillum dolore eu fugiat nulla pariatur."
        ),
        "category_slug": "categorie-b",
        "is_published": True,
    },
    {
        "title": "Service quatre",
        "description": (
            "Excepteur sint occaecat cupidatat non proident, sunt in culpa "
            "qui officia deserunt mollit anim id est laborum."
        ),
        "category_slug": "categorie-c",
        "is_published": False,
    },
]


def seed() -> None:
    with app.app_context():
        db.drop_all()
        db.create_all()

        slug_to_id: dict[str, int] = {}
        for entry in CATEGORIES:
            category = Category(name=entry["name"], slug=entry["slug"])
            db.session.add(category)
            db.session.flush()
            slug_to_id[category.slug] = category.id

        for entry in SERVICES:
            db.session.add(
                Service(
                    title=entry["title"],
                    description=entry["description"],
                    category_id=slug_to_id[entry["category_slug"]],
                    is_published=entry["is_published"],
                )
            )

        db.session.commit()
        print(f"✅ Inserted {len(CATEGORIES)} categories and {len(SERVICES)} services.")


if __name__ == "__main__":
    seed()
