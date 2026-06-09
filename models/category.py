"""Category — Postgres entity used to group services."""
from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import db


class Category(db.Model):
    """Category groups several services together (1-N relationship)."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(80), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(db.String(80), nullable=False, unique=True)

    services: Mapped[list["Service"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Category {self.slug}>"


class CategoryRepository:
    """CRUD operations for :class:`Category`."""

    def list_all(self) -> list[Category]:
        return db.session.query(Category).order_by(Category.name).all()

    def get(self, category_id: int) -> Category | None:
        return db.session.get(Category, category_id)

    def get_by_slug(self, slug: str) -> Category | None:
        return db.session.query(Category).filter_by(slug=slug).one_or_none()

    def create(self, name: str, slug: str) -> Category:
        category = Category(name=name.strip(), slug=slug.strip().lower())
        db.session.add(category)
        db.session.commit()
        return category

    def update(self, category_id: int, *, name: str, slug: str) -> Category | None:
        category = self.get(category_id)
        if category is None:
            return None
        category.name = name.strip()
        category.slug = slug.strip().lower()
        db.session.commit()
        return category

    def delete(self, category_id: int) -> bool:
        category = self.get(category_id)
        if category is None:
            return False
        db.session.delete(category)
        db.session.commit()
        return True
