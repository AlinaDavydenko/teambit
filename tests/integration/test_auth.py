userdata = {
    "first_name": "Alina",
    "last_name": "Davydenko",
    "nickname": "Li",
    "email": "Abc@gmail.com",
    "password": "12345678",
}

login_data = {"email": "Abc@gmail.com", "password": "12345678"}


def test_register_success(client):
    """Registration test"""
    response = client.post("/auth/register", json=userdata)
    assert response.status_code == 200
    assert response.json()["email"] == "Abc@gmail.com"


def test_register_duplicate_email(client):
    """Existiing Email registration"""
    # register
    response = client.post("/auth/register", json=userdata)

    # change nikname
    duplicate = {**userdata, "nickname": "different_nick"}

    # register with the same Email
    response = client.post("/auth/register", json=duplicate)
    assert response.status_code == 400


def test_register_duplicate_nickname(client):
    """Existing nickname registration"""
    # register
    response = client.post("/auth/register", json=userdata)

    # change Email
    duplicate = {**userdata, "email": "Acd@gmail.com"}

    # register with the same nickname
    response = client.post("/auth/register", json=duplicate)

    assert response.status_code == 400


def test_register_invalid_email(client):
    """Invalid email registration"""
    # send email without @
    invalid = {**userdata, "email": "notanemail"}
    response = client.post("/auth/register", json=invalid)
    assert response.status_code == 422


def test_register_short_password(client):
    """Short password registration"""
    # send password less then 8 symbols
    invalid_password = {**userdata, "password": "12345"}
    response = client.post("/auth/register", json=invalid_password)
    assert response.status_code == 422


def test_login_success(client):
    """Login"""
    # register
    response = client.post("/auth/register", json=userdata)

    # loggin
    login_response = client.post("/auth/login", json=login_data)

    assert login_response.status_code == 200
    assert isinstance(login_response.json(), str)
    assert len(login_response.json()) > 0


def test_incorrect_password(client):
    """Login with incorrect passwprd"""
    # register
    response = client.post("/auth/register", json=userdata)

    # login with incorrect password
    invalid_password = {**userdata, "password": "87654321567"}
    login_response = client.post("/auth/login", json=invalid_password)

    assert login_response.status_code == 401


def test_incorrect_email(client):
    """Login with incorrect Email"""
    # register
    response = client.post("/auth/register", json=userdata)

    # login with incorrect Email
    invalid_email = {**userdata, "email": "Sos@gmail.com"}
    login_response = client.post("/auth/login", json=invalid_email)

    assert login_response.status_code == 401
