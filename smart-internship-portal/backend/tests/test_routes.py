import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.config import db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_database():
    """Clean the test collections before each test run if needed"""
    db.students_collection.delete_many({})
    db.internships_collection.delete_many({})
    db.applications_collection.delete_many({})
    yield

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Smart Internship Portal API is running"}

def test_register_user():
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "securepassword",
        "university": "Test University"
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 200
    
    # Assert proper token format is returned
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user():
    # Setup test user directly in DB
    from backend.routes import pwd_context
    db.students_collection.insert_one({
        "name": "Test User",
        "email": "loginuser@example.com",
        "password": pwd_context.hash("loginpassword")
    })
    
    response = client.post(
        "/api/login",
        data={"username": "loginuser@example.com", "password": "loginpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    
def test_admin_stats():
    # Insert some mock data
    db.students_collection.insert_one({"name": "Stat User", "email": "stat@test.com"})
    db.internships_collection.insert_one({"title": "Role 1"})
    
    response = client.get("/api/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["totalStudents"] > 0
    assert data["totalInternships"] > 0
