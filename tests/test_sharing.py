def test_share_category_with_user(client, auth_headers, create_test_user):
    # Create a category
    cat_resp = client.post(
        "/inventory/categories",
        json={"name": "Shared Category"},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]

    # Create another user to share with
    user_b, _ = create_test_user(email="sharetarget@test.com", name="Target")

    response = client.post(
        f"/sharing/items/category/{cat_id}/share",
        json={"emails": ["sharetarget@test.com"]},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert len(response.json()) == 1


def test_submit_for_approval(client, auth_headers):
    cat_resp = client.post(
        "/inventory/categories",
        json={"name": "Approval Test"},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]

    response = client.post(
        f"/sharing/items/category/{cat_id}/submit",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Submitted for approval"


def test_admin_approve_item(client, auth_headers, admin_headers):
    # User creates and submits
    cat_resp = client.post(
        "/inventory/categories",
        json={"name": "To Approve"},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]

    client.post(
        f"/sharing/items/category/{cat_id}/submit",
        headers=auth_headers,
    )

    # Admin approves
    response = client.put(
        f"/sharing/approval-queue/category/{cat_id}",
        json={"action": "approve"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Item approved"


def test_admin_reject_item(client, auth_headers, admin_headers):
    cat_resp = client.post(
        "/inventory/categories",
        json={"name": "To Reject"},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]

    client.post(
        f"/sharing/items/category/{cat_id}/submit",
        headers=auth_headers,
    )

    response = client.put(
        f"/sharing/approval-queue/category/{cat_id}",
        json={"action": "reject"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Item rejected"


def test_approval_queue_requires_admin(client, auth_headers):
    response = client.get("/sharing/approval-queue", headers=auth_headers)
    assert response.status_code == 403


def test_approval_queue_with_filter(client, auth_headers, admin_headers):
    # Create and submit two items
    for name in ["Item A", "Item B"]:
        cat_resp = client.post(
            "/inventory/categories",
            json={"name": name},
            headers=auth_headers,
        )
        cat_id = cat_resp.json()["id"]
        client.post(
            f"/sharing/items/category/{cat_id}/submit",
            headers=auth_headers,
        )

    response = client.get(
        "/sharing/approval-queue?status=pending",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert len(response.json()) >= 2
    for item in response.json():
        assert item["approval_status"] == "pending"
