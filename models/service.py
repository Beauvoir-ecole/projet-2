"""Service — Postgres entity describing one offer of the catalogue."""
from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import db
from .category import Category


class Service(db.Model):
    """One service / product on display, attached to a category."""

    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(120), nullable=False)
    description: Mapped[str] = mapped_column(db.Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )

    category: Mapped[Category] = relationship(back_populates="services")

    def __repr__(self) -> str:
        return f"<Service {self.title!r}>"


class ServiceRepository:
    """CRUD operations for :class:`Service`.

    Methods using user input strip and validate values defensively
    (validate and check input before writing to the database).
    """

    MAX_TITLE_LENGTH = 120

    def list_published(self) -> list[Service]:
        return (
            db.session.query(Service)
            .filter(Service.is_published.is_(True))
            .order_by(Service.id)
            .all()
        )

    def list_all(self) -> list[Service]:
        return db.session.query(Service).order_by(Service.id).all()

    def get(self, service_id: int) -> Service | None:
        return db.session.get(Service, service_id)

    def create(
        self,
        *,
        title: str,
        description: str,
        category_id: int,
        is_published: bool = True,
    ) -> Service:
        title = self._validate_title(title)
        description = description.strip()
        service = Service(
            title=title,
            description=description,
            category_id=category_id,
            is_published=is_published,
        )
        db.session.add(service)
        db.session.commit()
        return service

    def update(
        self,
        service_id: int,
        *,
        title: str,
        description: str,
        category_id: int,
        is_published: bool,
    ) -> Service | None:
        service = self.get(service_id)
        if service is None:
            return None
        service.title = self._validate_title(title)
        service.description = description.strip()
        service.category_id = category_id
        service.is_published = is_published
        db.session.commit()
        return service

    def delete(self, service_id: int) -> bool:
        service = self.get(service_id)
        if service is None:
            return False
        db.session.delete(service)
        db.session.commit()
        return True

    def _validate_title(self, title: str) -> str:
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty.")
        if len(title) > self.MAX_TITLE_LENGTH:
            raise ValueError(f"Title cannot exceed {self.MAX_TITLE_LENGTH} characters.")
        return title
