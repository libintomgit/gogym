def test_register_returns_token(client):
    response = client.post(
        "/auth/register", json={
            "email": "new@test.com",
            "password": "secret123",
            "name": "New User",
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "new@test.com"

def test_duplicate_email_returns_409(client, test_user):
    user, _ = test_user
    response = client.post(
        "/auth/register", json={
            "email": user.email,
            "password": "other",
            "name": "Dup",
        }
    )
    assert response.status_code == 409