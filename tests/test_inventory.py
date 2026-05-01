def test_create_category_as_user(client, auth_headers):
    response = client.post(
        "/inventory/categories",
        json={"name": "Upper Body"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Upper Body"
    assert data["sharing_scope"] == "private"


def test_create_category_as_admin(client, admin_headers):
    response = client.post(
        "/inventory/categories",
        json={"name": "Lower Body"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["sharing_scope"] == "global"


def test_list_categories(client, auth_headers):
    # Create one first
    client.post(
        "/inventory/categories",
        json={"name": "Arms"},
        headers=auth_headers,
    )
    response = client.get("/inventory/categories", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_update_category(client, auth_headers):
    # Create
    create_resp = client.post(
        "/inventory/categories",
        json={"name": "Old Name"},
        headers=auth_headers,
    )
    cat_id = create_resp.json()["id"]

    # Update
    response = client.put(
        f"/inventory/categories/{cat_id}",
        json={"name": "New Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_delete_category(client, auth_headers):
    create_resp = client.post(
        "/inventory/categories",
        json={"name": "To Delete"},
        headers=auth_headers,
    )
    cat_id = create_resp.json()["id"]

    response = client.delete(
        f"/inventory/categories/{cat_id}",
        headers=auth_headers,
    )
    assert response.status_code == 204


def test_other_user_cannot_modify(client, auth_headers, create_test_user):
    # User A creates a category
    create_resp = client.post(
        "/inventory/categories",
        json={"name": "User A's Category"},
        headers=auth_headers,
    )
    cat_id = create_resp.json()["id"]

    # User B tries to update it
    _, token_b = create_test_user(email="userb@test.com", name="User B")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    response = client.put(
        f"/inventory/categories/{cat_id}",
        json={"name": "Hacked"},
        headers=headers_b,
    )
    assert response.status_code == 403


def test_unauthenticated_returns_401(client):
    response = client.get("/inventory/categories")
    assert response.status_code == 401  # HTTPBearer returns 403 when no token