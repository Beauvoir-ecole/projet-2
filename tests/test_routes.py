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
