"""Testimonial — MongoDB document stored in collection ``testimonials``.

Mongo is the right fit here because testimonials carry semi-structured
data (free-form comments, optional metadata) and don't need foreign keys.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from .db import get_mongo_db


@dataclass
class Testimonial:
    """In-memory representation of a testimonial document.

    Mongo stores ``_id`` as :class:`bson.ObjectId`; we expose it as ``id``
    (string) so templates and tests can ignore the BSON layer.
    """

    author: str
    comment: str
    rating: int
    is_approved: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: Optional[str] = None

    @classmethod
    def from_document(cls, document: dict) -> "Testimonial":
        return cls(
            id=str(document["_id"]),
            author=document["author"],
            comment=document["comment"],
            rating=int(document.get("rating", 0)),
            is_approved=bool(document.get("is_approved", False)),
            created_at=document.get("created_at", datetime.now(timezone.utc)),
        )


class TestimonialRepository:
    """CRUD operations for the ``testimonials`` collection.

    The repository performs input validation before any write
    (defensive programming).
    """

    COLLECTION = "testimonials"
    MIN_RATING = 1
    MAX_RATING = 5
    MAX_COMMENT_LENGTH = 1000

    def _collection(self):
        return get_mongo_db()[self.COLLECTION]

    def list_approved(self) -> list[Testimonial]:
        cursor = self._collection().find({"is_approved": True}).sort("created_at", -1)
        return [Testimonial.from_document(doc) for doc in cursor]

    def list_all(self) -> list[Testimonial]:
        cursor = self._collection().find().sort("created_at", -1)
        return [Testimonial.from_document(doc) for doc in cursor]

    def get(self, testimonial_id: str) -> Testimonial | None:
        try:
            oid = ObjectId(testimonial_id)
        except Exception:
            return None
        document = self._collection().find_one({"_id": oid})
        return Testimonial.from_document(document) if document else None

    def create(self, *, author: str, comment: str, rating: int) -> Testimonial:
        author = self._validate_text(author, "author", max_length=80)
        comment = self._validate_text(comment, "comment", max_length=self.MAX_COMMENT_LENGTH)
        rating = self._validate_rating(rating)
        document = {
            "author": author,
            "comment": comment,
            "rating": rating,
            "is_approved": False,
            "created_at": datetime.now(timezone.utc),
        }
        result = self._collection().insert_one(document)
        document["_id"] = result.inserted_id
        return Testimonial.from_document(document)

    def set_approved(self, testimonial_id: str, *, approved: bool) -> bool:
        try:
            oid = ObjectId(testimonial_id)
        except Exception:
            return False
        result = self._collection().update_one(
            {"_id": oid},
            {"$set": {"is_approved": bool(approved)}},
        )
        return result.matched_count == 1

    def delete(self, testimonial_id: str) -> bool:
        try:
            oid = ObjectId(testimonial_id)
        except Exception:
            return False
        result = self._collection().delete_one({"_id": oid})
        return result.deleted_count == 1

    def _validate_text(self, value: str, field_name: str, *, max_length: int) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string.")
        value = value.strip()
        if not value:
            raise ValueError(f"{field_name} cannot be empty.")
        if len(value) > max_length:
            raise ValueError(f"{field_name} cannot exceed {max_length} characters.")
        return value

    def _validate_rating(self, rating: int) -> int:
        try:
            rating = int(rating)
        except (TypeError, ValueError) as exc:
            raise ValueError("Rating must be an integer.") from exc
        if not self.MIN_RATING <= rating <= self.MAX_RATING:
            raise ValueError(
                f"Rating must be between {self.MIN_RATING} and {self.MAX_RATING}."
            )
        return rating
