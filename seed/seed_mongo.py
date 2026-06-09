"""Populate the Mongo database with fictional testimonials.

Run with:
    python seed/seed_mongo.py

This script is meant to be edited freely — change the list below to
match your project, or ask Claude / ChatGPT to rewrite the entries.
"""
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Allow running this file directly from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from models import TestimonialRepository
from models.db import get_mongo_db


TESTIMONIALS = [
    {
        "author": "Alice Dupont",
        "comment": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Service au top !",
        "rating": 5,
        "is_approved": True,
    },
    {
        "author": "Marc Bernard",
        "comment": "Sed do eiusmod tempor incididunt ut labore. Très bonne expérience globalement.",
        "rating": 4,
        "is_approved": True,
    },
    {
        "author": "Camille Lefèvre",
        "comment": "Ut enim ad minim veniam, quis nostrud exercitation. Rien à dire, je recommande.",
        "rating": 5,
        "is_approved": True,
    },
    {
        "author": "Léo Garcia",
        "comment": "Duis aute irure dolor in reprehenderit. Quelques détails à améliorer mais correct.",
        "rating": 3,
        "is_approved": False,
    },
]


def seed() -> None:
    if not os.environ.get("MONGO_URL"):
        print("⚠️  MONGO_URL n'est pas défini. Configure-le dans .env avant de relancer.")
        sys.exit(1)

    collection = get_mongo_db()[TestimonialRepository.COLLECTION]
    collection.delete_many({})

    now = datetime.now(timezone.utc)
    documents = []
    for index, entry in enumerate(TESTIMONIALS):
        documents.append(
            {
                "author": entry["author"],
                "comment": entry["comment"],
                "rating": entry["rating"],
                "is_approved": entry["is_approved"],
                "created_at": now - timedelta(days=index),
            }
        )

    collection.insert_many(documents)
    print(f"✅ Inserted {len(documents)} testimonials into Mongo.")


if __name__ == "__main__":
    seed()
