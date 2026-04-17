"""
Tests for error handling and edge cases.
"""
import pytest
from urllib.parse import quote


class TestParameterValidation:
    """Test suite for parameter validation and edge cases."""
    
    def test_signup_with_encoded_activity_name(self, client):
        """
        Test signup with URL-encoded activity names.
        
        Arrange: Prepare activity name with spaces
        Act: Sign up with URL-encoded activity name
        Assert: Verify signup succeeds with proper encoding
        """
        # Arrange
        activity_name = "Basketball Team"  # Has space
        email = "player@mergington.edu"
        
        # Act - Use URL encoding for spaces
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_unregister_with_encoded_activity_name(self, client):
        """
        Test unregister with URL-encoded activity names.
        
        Arrange: Sign up student, prepare URL-encoded activity name
        Act: Unregister with URL-encoded activity name
        Assert: Verify unregister succeeds with proper encoding
        """
        # Arrange
        activity_name = "Programming Class"  # Has space
        email = "programmer@mergington.edu"
        
        # Act - Sign up first
        client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email}
        )
        
        # Act - Unregister with encoding
        response = client.delete(
            f"/activities/{quote(activity_name)}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_signup_empty_email_param(self, client):
        """
        Test signup with empty email parameter.
        
        Arrange: Activity name ready, empty email
        Act: Send POST with empty email
        Assert: Verify request is processed (behavior depends on implementation)
        """
        # Arrange
        activity_name = "Basketball Team"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": ""}
        )
        
        # Assert - Empty email is technically valid in URL, may succeed or fail
        # This depends on implementation - documenting current behavior
        assert response.status_code in [200, 400, 422]
    
    def test_signup_very_long_email(self, client):
        """
        Test signup with extremely long email address.
        
        Arrange: Create long email string
        Act: Send signup request with long email
        Assert: Verify request is accepted or rejected gracefully
        """
        # Arrange
        activity_name = "Basketball Team"
        long_email = "a" * 200 + "@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": long_email}
        )
        
        # Assert - Should handle gracefully
        assert response.status_code in [200, 400, 422]


class TestActivityNameHandling:
    """Test suite for activity name handling edge cases."""
    
    def test_case_sensitive_activity_retrieval(self, client):
        """
        Test that activity names are case-sensitive.
        
        Arrange: Know exact activity name case
        Act: Try different casings
        Assert: Verify only exact case works
        """
        # Arrange
        correct_name = "Chess Club"
        email = "player@mergington.edu"
        
        # Act - Correct case
        response_correct = client.post(
            f"/activities/{quote(correct_name)}/signup",
            params={"email": "p1@example.com"}
        )
        
        # Act - Different case
        response_lower = client.post(
            f"/activities/{quote(correct_name.lower())}/signup",
            params={"email": "p2@example.com"}
        )
        
        # Assert - Correct case succeeds, different case fails
        assert response_correct.status_code == 200
        assert response_lower.status_code == 404
    
    def test_activity_name_with_special_chars(self, client):
        """
        Test activities with special characters in names.
        
        Arrange: Check if any activity has special chars
        Act: Try to sign up for such activity
        Assert: Verify URL encoding is handled properly
        """
        # Arrange - Get all activities to check names
        activities = client.get("/activities").json()
        email = "test@mergington.edu"
        
        # Act - Try signing up for each activity
        for activity_name in activities.keys():
            response = client.post(
                f"/activities/{quote(activity_name)}/signup",
                params={"email": f"special_{activity_name.replace(' ', '_')}@test.edu"}
            )
            
            # Assert - All activities accessible with proper encoding
            assert response.status_code != 404, f"Failed for {activity_name}"


class TestConcurrentOperations:
    """Test suite for handling rapid/concurrent-like operations."""
    
    def test_signup_immediately_after_unregister_same_student(self, client):
        """
        Test rapid signup after unregister of same student.
        
        Arrange: Student is registered
        Act: Unregister then immediately sign up
        Assert: Verify both operations succeed without interference
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act - Unregister
        unreg_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert - Unregister success
        assert unreg_response.status_code == 200
        
        # Act - Immediately sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Signup also succeeds
        assert signup_response.status_code == 200
        assert email in client.get("/activities").json()[activity_name]["participants"]
    
    def test_unregister_twice_same_student(self, client):
        """
        Test unregistering the same student twice.
        
        Arrange: Student is registered
        Act: Unregister, then try to unregister again
        Assert: First succeeds, second fails with 400
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act - First unregister
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert - First succeeds
        assert response1.status_code == 200
        
        # Act - Second unregister (should fail)
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert - Second fails with 400
        assert response2.status_code == 400
        assert "not registered" in response2.json()["detail"].lower()


class TestResponseFormats:
    """Test suite for response format consistency."""
    
    def test_signup_response_format(self, client):
        """
        Test that signup response has expected format.
        
        Arrange: Prepare signup request
        Act: Sign up student
        Assert: Verify response JSON structure
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "player@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Response format
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)
    
    def test_error_response_format(self, client):
        """
        Test that error responses have expected format.
        
        Arrange: Prepare invalid request
        Act: Make request to non-existent activity
        Assert: Verify error response JSON structure
        """
        # Arrange
        fake_activity = "Fake Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": email}
        )
        
        # Assert - Error response format
        assert response.status_code == 404
        data = response.json()
        assert isinstance(data, dict)
        assert "detail" in data
        assert isinstance(data["detail"], str)
    
    def test_activities_response_format(self, client):
        """
        Test that GET /activities response is properly formatted JSON.
        
        Arrange: Client ready
        Act: Get activities
        Assert: Verify response is valid JSON dict with expected structure
        """
        # Act
        response = client.get("/activities")
        
        # Assert - Response format
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
