import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.models import Base
from app.db.session import get_db

sys.path.insert(0, os.path.dirname(__file__))

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client):
    """Client with auth token"""
    client.post(
        "/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "nickname": "testuser",
            "email": "test@test.com",
            "password": "12345678",
        },
    )
    response = client.post(
        "/auth/login", json={"email": "test@test.com", "password": "12345678"}
    )
    token = response.json()
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
