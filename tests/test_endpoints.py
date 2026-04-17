"""
Tests for core endpoint functionality.
"""
import pytest


class TestRootEndpoint:
    """Test suite for GET / endpoint."""
    
    def test_root_redirect(self, client):
        """
        Test that GET / redirects to /static/index.html.
        
        Arrange: Client is ready
        Act: Send GET request to /
        Assert: Verify redirect status and location header
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers.get("location", "")


class TestActivitiesEndpoint:
    """Test suite for GET /activities endpoint."""
    
    def test_get_activities_returns_dict(self, client):
        """
        Test that GET /activities returns a JSON dictionary.
        
        Arrange: Client is ready
        Act: Send GET request to /activities
        Assert: Verify response is 200 and returns a dict
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    def test_get_activities_has_required_fields(self, client):
        """
        Test that each activity has required fields.
        
        Arrange: Client is ready
        Act: Send GET request to /activities
        Assert: Verify each activity has description, schedule, max_participants, participants
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert len(activities) > 0, "Should have at least one activity"
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data, f"{activity_name} missing 'description'"
            assert "schedule" in activity_data, f"{activity_name} missing 'schedule'"
            assert "max_participants" in activity_data, f"{activity_name} missing 'max_participants'"
            assert "participants" in activity_data, f"{activity_name} missing 'participants'"
    
    def test_get_activities_participants_is_list(self, client):
        """
        Test that participants field is always a list.
        
        Arrange: Client is ready
        Act: Send GET request to /activities
        Assert: Verify participants is a list for all activities
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants should be a list"
    
    def test_get_activities_max_participants_is_positive_int(self, client):
        """
        Test that max_participants is a positive integer.
        
        Arrange: Client is ready
        Act: Send GET request to /activities
        Assert: Verify max_participants is a positive int for all activities
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int), \
                f"{activity_name} max_participants should be an int"
            assert activity_data["max_participants"] > 0, \
                f"{activity_name} max_participants should be positive"
