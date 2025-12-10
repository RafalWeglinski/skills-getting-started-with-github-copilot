"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store the original state
    original_activities = {
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
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for getting activities"""
    
    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that GET /activities returns 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self, client, reset_activities):
        """Test that GET /activities returns expected activities"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
    
    def test_get_activities_participants_is_list(self, client, reset_activities):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_details in data.values():
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for signing up for an activity"""
    
    def test_signup_successful(self, client, reset_activities):
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
            "/activities/NonExistent%20Activity/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test signup with duplicate email"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_returns_correct_message(self, client, reset_activities):
        """Test that signup returns correct message"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "newstudent@mergington.edu" in data["message"]
        assert "Programming Class" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup adds participant to the activity"""
        email = "newstudent@mergington.edu"
        initial_count = len(activities["Chess Club"]["participants"])
        
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        final_count = len(activities["Chess Club"]["participants"])
        assert final_count == initial_count + 1
        assert email in activities["Chess Club"]["participants"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test that multiple students can sign up"""
        student1 = "student1@mergington.edu"
        student2 = "student2@mergington.edu"
        
        response1 = client.post(f"/activities/Gym%20Class/signup?email={student1}")
        response2 = client.post(f"/activities/Gym%20Class/signup?email={student2}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert student1 in activities["Gym Class"]["participants"]
        assert student2 in activities["Gym Class"]["participants"]
