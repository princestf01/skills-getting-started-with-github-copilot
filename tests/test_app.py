"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    global activities
    activities.clear()
    activities.update({
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
            "description": "Competitive basketball training and matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis lessons and tournament participation",
            "schedule": "Tuesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu", "sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts exploration",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["grace@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performances and acting workshops",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and scientific exploration",
            "schedule": "Fridays, 3:00 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        }
    })
    yield


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_all_activities(self, client):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_structure(self, client):
        """Test that activity structure is correct"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_activities_have_participants(self, client):
        """Test that activities have the correct initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_successful_signup(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup adds participant to the activity"""
        email = "newstudent@mergington.edu"
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]

    def test_duplicate_signup_fails(self, client):
        """Test that signing up twice fails"""
        email = "michael@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_to_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_with_full_activity(self, client):
        """Test signing up when activity is full"""
        # Add participants until full (max 12 for Chess Club, currently has 2)
        for i in range(10):
            client.post(
                "/activities/Basketball Team/signup",
                params={"email": f"student{i}@mergington.edu"}
            )
        
        # Basketball Team now has 11 participants (1 initial + 10 added), max is 15
        # Try to add one more participant that exceeds the limit
        # First fill it up completely
        response = None
        for i in range(10, 15):
            response = client.post(
                "/activities/Basketball Team/signup",
                params={"email": f"student{i}@mergington.edu"}
            )
        
        # Now try to add one more when full
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "overflow@mergington.edu"}
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"]


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_successful_unregister(self, client):
        """Test successfully unregistering from an activity"""
        email = "michael@mergington.edu"
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from the activity"""
        email = "michael@mergington.edu"
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregistering when not registered for activity"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_twice_fails(self, client):
        """Test that unregistering twice fails"""
        email = "michael@mergington.edu"
        # First unregister succeeds
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Second unregister fails
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 400


class TestSignupUnregisterFlow:
    """Tests for combined signup and unregister flows"""

    def test_signup_then_unregister(self, client):
        """Test signing up and then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Art Studio"
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]

    def test_signup_unregister_signup_again(self, client):
        """Test signup, unregister, and signup again"""
        email = "testuser@mergington.edu"
        activity = "Debate Team"
        
        # First signup
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Sign up again - should succeed
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
