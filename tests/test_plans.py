def test_create_plan_as_user(client, auth_headers):
    response = client.post(
        "/plans",
        json={"name": "Push Pull Legs", "description": "3-day split", "num_days": 3},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Push Pull Legs"
    assert data["sharing_scope"] == "private"
    assert data["num_days"] == 3


def test_create_plan_as_admin(client, admin_headers):
    response = client.post(
        "/plans",
        json={"name": "Beginner Plan", "num_days": 4},
        headers=admin_headers,
    )
    assert response.status_code == 201
    assert response.json()["sharing_scope"] == "global"


def test_list_plans(client, auth_headers):
    client.post(
        "/plans",
        json={"name": "Plan A", "num_days": 2},
        headers=auth_headers,
    )
    response = client.get("/plans", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_plan_by_id(client, auth_headers):
    create_resp = client.post(
        "/plans",
        json={"name": "My Plan", "num_days": 1},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    response = client.get(f"/plans/{plan_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "My Plan"


def test_update_plan(client, auth_headers):
    create_resp = client.post(
        "/plans",
        json={"name": "Old Plan", "num_days": 2},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    response = client.put(
        f"/plans/{plan_id}",
        json={"name": "Updated Plan"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Plan"


def test_delete_plan(client, auth_headers):
    create_resp = client.post(
        "/plans",
        json={"name": "Delete Me", "num_days": 1},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    response = client.delete(f"/plans/{plan_id}", headers=auth_headers)
    assert response.status_code == 204


def test_other_user_cannot_modify_plan(client, auth_headers, create_test_user):
    create_resp = client.post(
        "/plans",
        json={"name": "User A Plan", "num_days": 1},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    _, token_b = create_test_user(email="planb@test.com", name="User B")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    response = client.put(
        f"/plans/{plan_id}",
        json={"name": "Stolen"},
        headers=headers_b,
    )
    assert response.status_code == 403


def test_add_plan_day(client, auth_headers):
    create_resp = client.post(
        "/plans",
        json={"name": "Day Test", "num_days": 2},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    response = client.post(
        f"/plans/{plan_id}/days",
        json={"day_number": 1, "name": "Push Day"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["day_number"] == 1
    assert response.json()["name"] == "Push Day"


def test_delete_plan_cascades_days(client, auth_headers):
    create_resp = client.post(
        "/plans",
        json={"name": "Cascade Test", "num_days": 1},
        headers=auth_headers,
    )
    plan_id = create_resp.json()["id"]

    client.post(
        f"/plans/{plan_id}/days",
        json={"day_number": 1, "name": "Day 1"},
        headers=auth_headers,
    )

    response = client.delete(f"/plans/{plan_id}", headers=auth_headers)
    assert response.status_code == 204

    # Plan should be gone
    response = client.get(f"/plans/{plan_id}", headers=auth_headers)
    assert response.status_code == 404
