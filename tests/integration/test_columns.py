column_data = {"name": "Lavanda"}
rename_column = {"name": "Love"}
board_data = {"name": "Love", "color": "F7F2FC"}
user_a = {
    "first_name": "A",
    "last_name": "A",
    "nickname": "userA",
    "email": "a@test.com",
    "password": "12345678",
}

user_b = {
    "first_name": "B",
    "last_name": "B",
    "nickname": "userB",
    "email": "b@test.com",
    "password": "12345678",
}


def test_create_column(auth_client):
    """Create column"""
    # Create board first
    responce = auth_client.post("/boards/", json=board_data)
    board_id = responce.json()["board_id"]

    # Create column
    responce = auth_client.post(f"/boards/{board_id}/columns", json=column_data)

    assert responce.status_code == 200


def test_rename_column(auth_client):
    """Rename column"""
    # Create board first
    responce = auth_client.post("/boards/", json=board_data)
    board_id = responce.json()["board_id"]

    # Create column
    responce = auth_client.post(f"/boards/{board_id}/columns", json=column_data)
    column_id = responce.json()["column_id"]

    # Rename column
    responce = auth_client.patch(
        f"/boards/{board_id}/columns/{column_id}", json=rename_column
    )

    assert responce.status_code == 200
    assert responce.json()["name"] == "Love"


def test_get_all_columns(auth_client):
    """Get all columns"""
    # Create board first
    responce = auth_client.post("/boards/", json=board_data)
    board_id = responce.json()["board_id"]

    # Create column
    responce = auth_client.post(f"/boards/{board_id}/columns", json=column_data)

    # Get all columns
    responce = auth_client.get(f"/boards/{board_id}/columns")

    assert responce.status_code == 200


def test_delete_column(auth_client):
    """Delete one column"""
    # Create board first
    responce = auth_client.post("/boards/", json=board_data)
    board_id = responce.json()["board_id"]

    # Create column
    responce = auth_client.post(f"/boards/{board_id}/columns", json=column_data)
    column_id = responce.json()["column_id"]

    # Delete column
    responce = auth_client.delete(f"/boards/{board_id}/columns/{column_id}")

    assert responce.status_code == 200


def test_create_column_no_token(client):
    """Create column without token"""
    # Register and login to get token
    client.post(
        "/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "nickname": "testuser2",
            "email": "test2@test.com",
            "password": "12345678",
        },
    )
    token = client.post(
        "/auth/login", json={"email": "test2@test.com", "password": "12345678"}
    ).json()
    client.headers.update({"Authorization": f"Bearer {token}"})
    board_id = client.post("/boards/", json=board_data).json()["board_id"]

    # Remove token and try to create column
    client.headers.pop("Authorization")
    response = client.post(f"/boards/{board_id}/columns", json=column_data)
    assert response.status_code == 401


def test_get_else_board(client):
    """Get someone else's board"""
    # Register user A and create board
    client.post("/auth/register", json=user_a)
    token_a = client.post(
        "/auth/login", json={"email": "a@test.com", "password": "12345678"}
    ).json()
    client.headers.update({"Authorization": f"Bearer {token_a}"})
    board_id = client.post("/boards/", json=board_data).json()["board_id"]

    # Create column
    responce = client.post(f"/boards/{board_id}/columns", json=column_data)

    # Register user B and try to get user A's board
    client.post("/auth/register", json=user_b)
    token_b = client.post(
        "/auth/login", json={"email": "b@test.com", "password": "12345678"}
    ).json()
    client.headers.update({"Authorization": f"Bearer {token_b}"})

    # Create column
    responce = client.post(f"/boards/{board_id}/columns", json=column_data)

    response = client.get(f"/boards/{board_id}/columns")
    assert response.status_code == 403
