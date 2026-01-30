import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import copy

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    # Reset activities to original state before each test
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
        },
        "Basketball Team": {
            "description": "Competitive basketball team for school tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and play friendly matches",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media art",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["amelia@mergington.edu"]
        },
        "Music Band": {
            "description": "Join the school band and perform at school events",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["alexander@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["charlotte@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Clear and restore activities
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that get activities returns 200 status"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that get activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that activities list contains expected activity names"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Music Band",
            "Debate Club",
            "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in activities
    
    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_returns_200(self, client):
        """Test signing up a new participant returns 200"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_signup_new_participant_returns_success_message(self, client):
        """Test signup returns success message"""
        # Use an activity with fewer participants to avoid duplicates
        email = "brandnewtester@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_duplicate_participant_returns_400(self, client):
        """Test signing up an existing participant returns 400"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
    
    def test_signup_duplicate_participant_returns_error_message(self, client):
        """Test duplicate signup returns appropriate error message"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_signup_nonexistent_activity_returns_error_message(self, client):
        """Test nonexistent activity returns appropriate error message"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]
    
    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds participant to activity"""
        email = "testuser@mergington.edu"
        
        # Sign up
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Tennis Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_returns_200(self, client):
        """Test unregistering an existing participant returns 200"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_unregister_existing_participant_returns_success_message(self, client):
        """Test unregister returns success message"""
        # Use a participant we know exists
        email = "daniel@mergington.edu"
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_unregister_nonexistent_participant_returns_400(self, client):
        """Test unregistering non-existent participant returns 400"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notinactivity@mergington.edu"}
        )
        assert response.status_code == 400
    
    def test_unregister_nonexistent_participant_returns_error_message(self, client):
        """Test unregister nonexistent participant returns appropriate error"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notinactivity@mergington.edu"}
        )
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test unregistering from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_unregister_removes_participant_from_activity(self, client):
        """Test that unregister actually removes participant from activity"""
        # First add a participant
        email = "tempuser@mergington.edu"
        client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        
        # Verify they were added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Programming Class"]["participants"]
        
        # Now unregister them
        response = client.post(
            "/activities/Programming Class/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify they were removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Programming Class"]["participants"]


class TestRoot:
    """Tests for GET / endpoint"""
    
    def test_root_returns_redirect(self, client):
        """Test that root endpoint returns a redirect"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [301, 302, 303, 307, 308]
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert "/static/index.html" in response.headers["location"]
