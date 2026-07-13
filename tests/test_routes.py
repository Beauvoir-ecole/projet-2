"""Smoke tests for the public routes.

These check that the controllers wire correctly to the views, not the
correctness of the views themselves.
"""


def test_home_responds_ok(client):
    response = client.get("/")
    assert response.status_code == 200


def test_about_responds_ok(client):
    response = client.get("/a-propos")
    assert response.status_code == 200


def test_services_responds_ok(client):
    response = client.get("/services")
    assert response.status_code == 200


def test_gallery_responds_ok(client):
    response = client.get("/galerie")
    assert response.status_code == 200


def test_404_when_unknown_route(client):
    response = client.get("/route-qui-nexiste-pas")
    assert response.status_code == 404


def test_admin_requires_login(client):
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


# ---------------------------------------------------------------------------
# /temoignages — seule route utilisant Mongo. On mocke le repository pour
# tester le controleur sans cluster Mongo (couverture manquante).
# ---------------------------------------------------------------------------
import app as app_module


def test_testimonials_get_ok(client, monkeypatch):
    monkeypatch.setattr(app_module.testimonials_repo, "list_approved", lambda: [])
    response = client.get("/temoignages")
    assert response.status_code == 200


def test_testimonials_post_valid_redirects(client, monkeypatch):
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(app_module.testimonials_repo, "create", fake_create)
    monkeypatch.setattr(app_module.testimonials_repo, "list_approved", lambda: [])
    response = client.post(
        "/temoignages",
        data={"author": "Alice", "comment": "Super", "rating": "5"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert captured["author"] == "Alice"


def test_testimonials_post_invalid_is_handled(client, monkeypatch):
    def fake_create(**kwargs):
        raise ValueError("Rating must be between 1 and 5.")

    monkeypatch.setattr(app_module.testimonials_repo, "create", fake_create)
    monkeypatch.setattr(app_module.testimonials_repo, "list_approved", lambda: [])
    response = client.post(
        "/temoignages",
        data={"author": "Bob", "comment": "x", "rating": "9"},
        follow_redirects=False,
    )
    # L'erreur de validation est capturee (flash) et la route redirige quand meme.
    assert response.status_code == 302


def test_testimonials_returns_503_when_mongo_down(client, monkeypatch):
    def boom():
        raise RuntimeError("MONGO_URL is not set.")

    monkeypatch.setattr(app_module.testimonials_repo, "list_approved", boom)
    response = client.get("/temoignages")
    assert response.status_code == 503
