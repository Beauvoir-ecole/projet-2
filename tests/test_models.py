"""Unit tests for the data layer.

Covers:
  - Postgres entities: Service + Category creation, FK, validation.
  - Mongo entity: Testimonial validation (the Mongo client itself is
    not tested here — that would require a live cluster).
"""
import pytest
from sqlalchemy.exc import IntegrityError

from models import (
    Category,
    CategoryRepository,
    Service,
    ServiceRepository,
    TestimonialRepository,
    db,
)


@pytest.fixture
def category(app):
    repo = CategoryRepository()
    return repo.create(name="Test", slug="test")


def test_category_create_and_get(app):
    repo = CategoryRepository()
    category = repo.create(name="Catégorie X", slug="categorie-x")
    assert category.id is not None
    assert repo.get(category.id).name == "Catégorie X"


def test_service_accepts_existing_category(app, category):
    repo = ServiceRepository()
    service = repo.create(
        title="Service un",
        description="Lorem",
        category_id=category.id,
    )
    assert service.id is not None
    assert service.category_id == category.id


def test_service_rejects_unknown_category(app):
    """Un service référençant une catégorie inexistante doit être refusé
    par la contrainte de clé étrangère (nécessite PRAGMA foreign_keys=ON)."""
    repo = ServiceRepository()
    with pytest.raises(IntegrityError):
        repo.create(title="Orphelin", description="x", category_id=999999)
    db.session.rollback()


def test_service_rejects_empty_title(app, category):
    repo = ServiceRepository()
    with pytest.raises(ValueError):
        repo.create(title="   ", description="x", category_id=category.id)


def test_service_rejects_too_long_title(app, category):
    repo = ServiceRepository()
    with pytest.raises(ValueError):
        repo.create(
            title="x" * (ServiceRepository.MAX_TITLE_LENGTH + 1),
            description="x",
            category_id=category.id,
        )


def test_testimonial_validation_rejects_bad_rating():
    repo = TestimonialRepository()
    with pytest.raises(ValueError):
        repo._validate_rating(0)
    with pytest.raises(ValueError):
        repo._validate_rating(6)
    assert repo._validate_rating(3) == 3


def test_testimonial_validation_rejects_empty_text():
    repo = TestimonialRepository()
    with pytest.raises(ValueError):
        repo._validate_text("   ", "author", max_length=80)
