board_data = {"name": "Love", "color": "F7F2FC"}
column_data = {"name": "To Do"}
move_data = {"column_id": 1, "position": 1}
card_data = {
    "name": "Fix bug",
    "color": "F7F2FC",
    "task_description": "Fix the login bug",
    "priority": 1,
    "deadline": "2026-12-01T00:00:00",
    "tags": "bug, fix",
}
card_update_data = {"name": "Fix bug updated", "color": "F5EEDF"}


def test_create_card(auth_client):
    """Create a card"""
    # Create board first
    responce = auth_client.post("/boards/", json=board_data)
    board_id = responce.json()["board_id"]

    # Create column
    responce = auth_client.post(f"/boards/{board_id}/columns", json=column_data)
    column_id = responce.json()["column_id"]

    # Create a card
    responce = auth_client.post(f"/cards/columns/{column_id}/card", json=card_data)

    assert responce.status_code == 200


def test_get_all_card(auth_client):
    """Get all cards"""
    # Create board first
    responce = auth_client.post("/boards/", json=board_data)
    board_id = responce.json()["board_id"]

    # Create column
    responce = auth_client.post(f"/boards/{board_id}/columns", json=column_data)
    column_id = responce.json()["column_id"]

    # Create a card
    responce = auth_client.post(f"/cards/columns/{column_id}/card", json=card_data)

    # Get all cards
    responce = auth_client.get(f"/cards/columns/{column_id}/cards")

    assert responce.status_code == 200


def test_update_card(auth_client):
    """Update a card"""
    # Create board first
    responce = auth_client.post("/boards/", json=board_data)
    board_id = responce.json()["board_id"]

    # Create column
    responce = auth_client.post(f"/boards/{board_id}/columns", json=column_data)
    column_id = responce.json()["column_id"]

    # Create a card
    responce = auth_client.post(f"/cards/columns/{column_id}/card", json=card_data)
    card_id = responce.json()["id"]

    # Update a card
    responce = auth_client.patch(f"/cards/{card_id}", json=card_update_data)

    assert responce.status_code == 200


def test_delete_card(auth_client):
    """Delete card"""
    # Create board first
    responce = auth_client.post("/boards/", json=board_data)
    board_id = responce.json()["board_id"]

    # Create column
    responce = auth_client.post(f"/boards/{board_id}/columns", json=column_data)
    column_id = responce.json()["column_id"]

    # Create a card
    responce = auth_client.post(f"/cards/columns/{column_id}/card", json=card_data)
    card_id = responce.json()["id"]

    # Delete a card
    responce = auth_client.delete(f"/cards/{card_id}")

    assert responce.status_code == 200


def test_move_card(auth_client):
    """Move card to another column"""
    # Create board first
    responce = auth_client.post("/boards/", json=board_data)
    board_id = responce.json()["board_id"]

    # Create first column
    responce = auth_client.post(f"/boards/{board_id}/columns", json=column_data)
    column_id = responce.json()["column_id"]

    # Create second column
    responce = auth_client.post(f"/boards/{board_id}/columns", json={"name": "Done"})
    new_column_id = responce.json()["column_id"]

    # Create a card in first column
    responce = auth_client.post(f"/cards/columns/{column_id}/card", json=card_data)
    card_id = responce.json()["id"]

    # Move the card to second column
    move_data = {"column_id": new_column_id, "position": 1}
    responce = auth_client.patch(f"/cards/{card_id}/move", json=move_data)

    assert responce.status_code == 200


def test_create_card_no_token(client):
    """Create card without token"""
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

    response = client.post(f"/boards/{board_id}/columns", json=column_data)
    column_id = response.json()["column_id"]

    client.headers.pop("Authorization")
    response = client.post(f"/cards/columns/{column_id}/card", json=card_data)

    assert response.status_code == 401
