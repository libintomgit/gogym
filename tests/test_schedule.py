from datetime import date, timedelta


def _create_plan_with_day(client, headers):
    """Helper to create a plan with one day."""
    plan_resp = client.post(
        "/plans",
        json={"name": "Test Plan", "num_days": 1},
        headers=headers,
    )
    plan_id = plan_resp.json()["id"]

    day_resp = client.post(
        f"/plans/{plan_id}/days",
        json={"day_number": 1, "name": "Day 1"},
        headers=headers,
    )
    day_id = day_resp.json()["id"]
    return plan_id, day_id


def test_assign_single_day(client, auth_headers):
    plan_id, day_id = _create_plan_with_day(client, auth_headers)

    response = client.post(
        "/schedule",
        json={
            "plan_day_id": day_id,
            "plan_id": plan_id,
            "scheduled_date": "2026-06-01",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["scheduled_date"] == "2026-06-01"


def test_second_workout_without_force_returns_409(client, auth_headers):
    plan_id, day_id = _create_plan_with_day(client, auth_headers)

    # First workout
    client.post(
        "/schedule",
        json={"plan_day_id": day_id, "plan_id": plan_id, "scheduled_date": "2026-06-02"},
        headers=auth_headers,
    )

    # Second without force
    response = client.post(
        "/schedule",
        json={"plan_day_id": day_id, "plan_id": plan_id, "scheduled_date": "2026-06-02"},
        headers=auth_headers,
    )
    assert response.status_code == 409


def test_second_workout_with_force_succeeds(client, auth_headers):
    plan_id, day_id = _create_plan_with_day(client, auth_headers)

    client.post(
        "/schedule",
        json={"plan_day_id": day_id, "plan_id": plan_id, "scheduled_date": "2026-06-03"},
        headers=auth_headers,
    )

    response = client.post(
        "/schedule",
        json={"plan_day_id": day_id, "plan_id": plan_id, "scheduled_date": "2026-06-03", "force": True},
        headers=auth_headers,
    )
    assert response.status_code == 201


def test_third_workout_always_rejected(client, auth_headers):
    plan_id, day_id = _create_plan_with_day(client, auth_headers)
    target_date = "2026-06-04"

    # First
    client.post(
        "/schedule",
        json={"plan_day_id": day_id, "plan_id": plan_id, "scheduled_date": target_date},
        headers=auth_headers,
    )
    # Second with force
    client.post(
        "/schedule",
        json={"plan_day_id": day_id, "plan_id": plan_id, "scheduled_date": target_date, "force": True},
        headers=auth_headers,
    )
    # Third
    response = client.post(
        "/schedule",
        json={"plan_day_id": day_id, "plan_id": plan_id, "scheduled_date": target_date, "force": True},
        headers=auth_headers,
    )
    assert response.status_code == 409


def test_get_schedule_range(client, auth_headers):
    plan_id, day_id = _create_plan_with_day(client, auth_headers)

    client.post(
        "/schedule",
        json={"plan_day_id": day_id, "plan_id": plan_id, "scheduled_date": "2026-07-01"},
        headers=auth_headers,
    )
    client.post(
        "/schedule",
        json={"plan_day_id": day_id, "plan_id": plan_id, "scheduled_date": "2026-07-03"},
        headers=auth_headers,
    )

    response = client.get(
        "/schedule?start_date=2026-07-01&end_date=2026-07-03",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_schedule(client, auth_headers):
    plan_id, day_id = _create_plan_with_day(client, auth_headers)

    create_resp = client.post(
        "/schedule",
        json={"plan_day_id": day_id, "plan_id": plan_id, "scheduled_date": "2026-08-01"},
        headers=auth_headers,
    )
    schedule_id = create_resp.json()["id"]

    response = client.delete(f"/schedule/{schedule_id}", headers=auth_headers)
    assert response.status_code == 204


def test_assign_full_plan(client, auth_headers):
    # Create a plan with 3 days
    plan_resp = client.post(
        "/plans",
        json={"name": "3 Day Plan", "num_days": 3},
        headers=auth_headers,
    )
    plan_id = plan_resp.json()["id"]

    for i in range(1, 4):
        client.post(
            f"/plans/{plan_id}/days",
            json={"day_number": i, "name": f"Day {i}"},
            headers=auth_headers,
        )

    response = client.post(
        "/schedule/plan",
        json={"plan_id": plan_id, "start_date": "2026-09-01"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert len(response.json()) == 3
