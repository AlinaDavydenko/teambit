board_data_1 = {"name": "Love", "color": "F7F2FC"}
board_data_2 = {"name": "Lavanda", "color": "F7F2FC"}

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


def test_create_board(auth_client):
    """Createion board's test"""
    responce = auth_client.post("/boards/", json=board_data_1)
    assert responce.status_code == 200


def test_get_all_boards(auth_client):
    """Get all boards"""
    # Create board first
    auth_client.post("/boards/", json=board_data_1)

    # Get all boards
    response = auth_client.get("/boards/")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_one_board(auth_client):
    """Get one board"""
    # Create board first
    response = auth_client.post("/boards/", json=board_data_1)
    board_id = response.json()["board_id"]

    # Get one board
    response = auth_client.get(f"/boards/{board_id}")

    assert response.status_code == 200
    assert response.json()["board_id"] == board_id


def test_delete_one_board(auth_client):
    """Delete a board"""
    # Create board first
    response = auth_client.post("/boards/", json=board_data_1)
    board_id = response.json()["board_id"]

    # Delete one board
    response = auth_client.delete(f"/boards/{board_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Board deleted successfully"


# Bad one


def test_create_board_no_token(client):
    """Create board without token"""
    response = client.post("/boards/", json=board_data_1)
    assert response.status_code == 401


def test_get_else_board(client):
    """Get someone else's board"""
    # Register user A and create board
    client.post("/auth/register", json=user_a)
    token_a = client.post(
        "/auth/login", json={"email": "a@test.com", "password": "12345678"}
    ).json()
    client.headers.update({"Authorization": f"Bearer {token_a}"})
    board_id = client.post("/boards/", json=board_data_1).json()["board_id"]

    # Register user B and try to get user A's board
    client.post("/auth/register", json=user_b)
    token_b = client.post(
        "/auth/login", json={"email": "b@test.com", "password": "12345678"}
    ).json()
    client.headers.update({"Authorization": f"Bearer {token_b}"})

    response = client.get(f"/boards/{board_id}")
    assert response.status_code == 403


def test_get_nonexistent_board(auth_client):
    """Get board that doesn't exist"""
    # Get one board
    board_id = 1
    response = auth_client.get(f"/boards/{board_id}")

    assert response.status_code == 404


def test_delete_else_board(client):
    """Delete someone else's board"""
    # Register user A and create board
    client.post("/auth/register", json=user_a)
    token_a = client.post(
        "/auth/login", json={"email": "a@test.com", "password": "12345678"}
    ).json()
    client.headers.update({"Authorization": f"Bearer {token_a}"})
    board_id = client.post("/boards/", json=board_data_1).json()["board_id"]

    # Register user B and try to delete user A's board
    client.post("/auth/register", json=user_b)
    token_b = client.post(
        "/auth/login", json={"email": "b@test.com", "password": "12345678"}
    ).json()
    client.headers.update({"Authorization": f"Bearer {token_b}"})

    # Delete the board
    response = client.delete(f"/boards/{board_id}")

    assert response.status_code == 403
