"""
Tests for the Mergington High School Activities API

This test module uses pytest and FastAPI's TestClient to test all API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Save initial state
    initial_state = {
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
            "description": "Competitive basketball team for school tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis training and friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["anna@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performances and acting workshops",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["carolina@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["marco@mergington.edu", "julia@mergington.edu"]
        },
        "Science Club": {
            "description": "Scientific experiments and STEM projects",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["pedro@mergington.edu"]
        }
    }
    
    # Clear and restore activities
    activities.clear()
    activities.update(initial_state)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that /activities returns a dictionary of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_info in data.items():
            assert "description" in activity_info
            assert "schedule" in activity_info
            assert "max_participants" in activity_info
            assert "participants" in activity_info
            assert isinstance(activity_info["participants"], list)
    
    def test_get_activities_contains_expected_activities(self, client, reset_activities):
        """Test that expected activities are present"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", 
            "Basketball Team", "Tennis Club", "Drama Club",
            "Art Studio", "Debate Team", "Science Club"
        ]
        
        for activity_name in expected_activities:
            assert activity_name in data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_registered(self, client, reset_activities):
        """Test signup when student is already registered"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """Test that signup adds participant to the activities list"""
        email = "testyuser@mergington.edu"
        initial_count = len(activities["Programming Class"]["participants"])
        
        response = client.post(
            "/activities/Programming%20Class/signup?email=testyuser@mergington.edu"
        )
        
        assert response.status_code == 200
        assert len(activities["Programming Class"]["participants"]) == initial_count + 1
        assert email in activities["Programming Class"]["participants"]
    
    def test_signup_with_different_activities(self, client, reset_activities):
        """Test signup for different activities"""
        email = "multiactivity@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Art%20Studio/signup?email=multiactivity@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Basketball%20Team/signup?email=multiactivity@mergington.edu"
        )
        assert response2.status_code == 200
        
        assert email in activities["Art Studio"]["participants"]
        assert email in activities["Basketball Team"]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/remove endpoint"""
    
    def test_remove_participant_success(self, client, reset_activities):
        """Test successful removal of a participant"""
        response = client.delete(
            "/activities/Chess%20Club/remove?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_remove_activity_not_found(self, client, reset_activities):
        """Test removal from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/remove?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_remove_participant_not_found(self, client, reset_activities):
        """Test removal of non-existent participant"""
        response = client.delete(
            "/activities/Chess%20Club/remove?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student not found in this activity"
    
    def test_remove_decreases_participant_count(self, client, reset_activities):
        """Test that removal decreases participant count"""
        initial_count = len(activities["Drama Club"]["participants"])
        
        response = client.delete(
            "/activities/Drama%20Club/remove?email=lucas@mergington.edu"
        )
        
        assert response.status_code == 200
        assert len(activities["Drama Club"]["participants"]) == initial_count - 1
    
    def test_remove_all_participants(self, client, reset_activities):
        """Test removing all participants from an activity"""
        participants = list(activities["Tennis Club"]["participants"])
        
        for participant in participants:
            response = client.delete(
                f"/activities/Tennis%20Club/remove?email={participant}"
            )
            assert response.status_code == 200
        
        assert len(activities["Tennis Club"]["participants"]) == 0


class TestIntegration:
    """Integration tests combining signup and removal"""
    
    def test_signup_then_remove(self, client, reset_activities):
        """Test signup followed by removal"""
        email = "testuser@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            "/activities/Art%20Studio/signup?email=testuser@mergington.edu"
        )
        assert signup_response.status_code == 200
        assert email in activities["Art Studio"]["participants"]
        
        # Remove
        remove_response = client.delete(
            "/activities/Art%20Studio/remove?email=testuser@mergington.edu"
        )
        assert remove_response.status_code == 200
        assert email not in activities["Art Studio"]["participants"]
    
    def test_multiple_signups_and_removals(self, client, reset_activities):
        """Test multiple signup and removal operations"""
        emails = [
            "user1@mergington.edu",
            "user2@mergington.edu",
            "user3@mergington.edu"
        ]
        
        # Sign up all
        for email in emails:
            response = client.post(
                f"/activities/Science%20Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all are registered
        for email in emails:
            assert email in activities["Science Club"]["participants"]
        
        # Remove some
        remove_response = client.delete(
            "/activities/Science%20Club/remove?email=user1@mergington.edu"
        )
        assert remove_response.status_code == 200
        
        # Verify removal
        assert "user1@mergington.edu" not in activities["Science Club"]["participants"]
        assert "user2@mergington.edu" in activities["Science Club"]["participants"]
        assert "user3@mergington.edu" in activities["Science Club"]["participants"]
