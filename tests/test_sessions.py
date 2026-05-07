import uuid


def _setup_session(client, auth_headers):
    """Create a plan with a day and return plan_day_id."""
    plan_resp = client.post(
        "/plans",
        json={"name": "Session Plan", "num_days": 1},
        headers=auth_headers,
    )
    plan_id = plan_resp.json()["id"]

    day_resp = client.post(
        f"/plans/{plan_id}/days",
        json={"day_number": 1, "name": "Chest Day"},
        headers=auth_headers,
    )
    return day_resp.json()["id"]


def test_start_session(client, auth_headers):
    day_id = _setup_session(client, auth_headers)

    response = client.post(
        "/sessions",
        json={"plan_day_id": day_id, "session_date": "2026-05-07"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["plan_day_id"] == day_id


def test_log_set(client, auth_headers, db):
    day_id = _setup_session(client, auth_headers)

    # Create an exercise to log against
    cat_resp = client.post(
        "/inventory/categories",
        json={"name": "Chest"},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]

    sub_resp = client.post(
        f"/inventory/categories/{cat_id}/subcategories",
        json={"name": "Press"},
        headers=auth_headers,
    )
    sub_id = sub_resp.json()["id"]

    ex_resp = client.post(
        f"/inventory/subcategories/{sub_id}/exercises",
        json={"name": "Bench Press", "target_muscles": "Chest, Triceps"},
        headers=auth_headers,
    )
    exercise_id = ex_resp.json()["id"]

    # Start session
    session_resp = client.post(
        "/sessions",
        json={"plan_day_id": day_id, "session_date": "2026-05-07"},
        headers=auth_headers,
    )
    session_id = session_resp.json()["id"]

    # Log a set
    response = client.post(
        f"/sessions/{session_id}/sets",
        json={
            "exercise_id": exercise_id,
            "set_number": 1,
            "reps_performed": 10,
            "weight": 60.0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert float(response.json()["weight"]) == 60.0
    assert response.json()["reps_performed"] == 10


def test_weight_must_be_positive(client, auth_headers):
    day_id = _setup_session(client, auth_headers)

    session_resp = client.post(
        "/sessions",
        json={"plan_day_id": day_id, "session_date": "2026-05-07"},
        headers=auth_headers,
    )
    session_id = session_resp.json()["id"]

    response = client.post(
        f"/sessions/{session_id}/sets",
        json={
            "exercise_id": str(uuid.uuid4()),
            "set_number": 1,
            "reps_performed": 10,
            "weight": 0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_complete_session(client, auth_headers):
    day_id = _setup_session(client, auth_headers)

    session_resp = client.post(
        "/sessions",
        json={"plan_day_id": day_id, "session_date": "2026-05-07"},
        headers=auth_headers,
    )
    session_id = session_resp.json()["id"]

    response = client.put(
        f"/sessions/{session_id}/complete",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["completed_at"] is not None


def test_end_session_early(client, auth_headers):
    day_id = _setup_session(client, auth_headers)

    session_resp = client.post(
        "/sessions",
        json={"plan_day_id": day_id, "session_date": "2026-05-07"},
        headers=auth_headers,
    )
    session_id = session_resp.json()["id"]

    response = client.put(
        f"/sessions/{session_id}/end",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "partial"
    assert response.json()["completed_at"] is not None


def test_get_session_history(client, auth_headers):
    day_id = _setup_session(client, auth_headers)

    # Create and complete a session
    session_resp = client.post(
        "/sessions",
        json={"plan_day_id": day_id, "session_date": "2026-05-01"},
        headers=auth_headers,
    )
    session_id = session_resp.json()["id"]
    client.put(f"/sessions/{session_id}/complete", headers=auth_headers)

    response = client.get("/sessions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["page"] == 1
