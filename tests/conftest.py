"""
Shared test fixtures and configuration for the test suite.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provide a TestClient for making HTTP requests to the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    Fixture that provides a fresh set of activities to each test.
    Clears the in-memory activities dictionary before each test to prevent
    state pollution between tests.
    
    Yields a minimal set of test activities.
    """
    # Store original activities
    original = activities.copy()
    
    # Clear and reset with minimal test data
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["alice@test.edu", "bob@test.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["charlie@test.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": []
        }
    })
    
    yield activities
    
    # Restore original activities after test
    activities.clear()
    activities.update(original)


@pytest.fixture
def client_with_fresh_activities(client, fresh_activities):
    """
    Convenience fixture combining TestClient and fresh activities.
    Use this in tests that need both.
    """
    return client
