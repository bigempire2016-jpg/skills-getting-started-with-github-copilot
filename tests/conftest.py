"""
Pytest configuration and shared fixtures for FastAPI tests.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture: TestClient for making requests to the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def activities_fixture():
    """
    Fixture: Sample activities data for testing.
    Returns a fresh dict with test data for each test.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice basketball skills and compete in games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
    }


@pytest.fixture
def test_email():
    """Fixture: Standard test email for reuse across tests."""
    return "test@mergington.edu"


@pytest.fixture
def test_activity_name():
    """Fixture: Standard test activity name for reuse across tests."""
    return "Chess Club"
