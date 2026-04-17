"""
Tests for unregister (delete) endpoint functionality.
"""
import pytest


class TestUnregisterSuccess:
    """Test suite for successful unregister scenarios."""
    
    def test_unregister_success(self, client):
        """
        Test successful unregister from an activity.
        
        Arrange: Activity has a participant
        Act: Send DELETE request to unregister endpoint
        Assert: Verify 200 response and success message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email in response.json()["message"]
        assert activity_name in response.json()["message"]
    
    def test_unregister_removes_email_from_participants(self, client):
        """
        Test that unregister actually removes email from participants.
        
        Arrange: Get initial activity state
        Act: Unregister a student
        Assert: Verify email is removed from participants list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act - Get initial state
        response_before = client.get("/activities")
        initial_participants = response_before.json()[activity_name]["participants"]
        assert email in initial_participants
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Act - Get final state
        response_after = client.get("/activities")
        final_participants = response_after.json()[activity_name]["participants"]
        
        # Assert
        assert unregister_response.status_code == 200
        assert email not in final_participants
        assert len(final_participants) == len(initial_participants) - 1
    
    def test_unregister_then_signup_again(self, client):
        """
        Test that student can re-signup after unregistering.
        
        Arrange: Student is registered
        Act: Unregister student, then sign them up again
        Assert: Verify both operations succeed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Act - Sign up again
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert signup_response.status_code == 200
        
        # Verify email is back in participants
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]


class TestUnregisterErrors:
    """Test suite for unregister error scenarios."""
    
    def test_unregister_nonexistent_activity(self, client):
        """
        Test unregister from non-existent activity returns 404.
        
        Arrange: Prepare fake activity name
        Act: Send DELETE request for non-existent activity
        Assert: Verify 404 response
        """
        # Arrange
        fake_activity = "Fake Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{fake_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered_student(self, client):
        """
        Test unregister for student not in participants returns 400.
        
        Arrange: Student has not signed up for activity
        Act: Send DELETE request for student not in participants
        Assert: Verify 400 response with appropriate message
        """
        # Arrange
        activity_name = "Basketball Team"  # Empty activity
        email = "not_registered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_with_special_chars_in_email(self, client):
        """
        Test unregister with special characters in email (URL encoding).
        
        Arrange: Sign up student with special chars email, then unregister
        Act: Unregister with URL-encoded email
        Assert: Verify unregister succeeds with proper encoding
        """
        # Arrange
        activity_name = "Art Club"
        email = "artist+pro@mergington.edu"
        
        # Act - Sign up first
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Act - Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify email is removed
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]


class TestUnregisterEdgeCases:
    """Test suite for unregister edge cases."""
    
    def test_unregister_one_participant_keeps_others(self, client):
        """
        Test that unregistering one student doesn't affect others.
        
        Arrange: Activity has multiple participants
        Act: Unregister one specific student
        Assert: Verify other participants remain in the list
        """
        # Arrange
        activity_name = "Gym Class"
        participant_to_remove = "john@mergington.edu"
        other_participant = "olivia@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": participant_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify removal and that others remain
        activities = client.get("/activities").json()
        assert participant_to_remove not in activities[activity_name]["participants"]
        assert other_participant in activities[activity_name]["participants"]
    
    def test_unregister_activity_name_case_sensitive(self, client):
        """
        Test that activity name lookup is case-sensitive in unregister.
        
        Arrange: Exact activity name is "Chess Club"
        Act: Try to unregister with different case
        Assert: Verify 404 (case-sensitive lookup)
        """
        # Arrange
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/chess%20club/unregister",  # lowercase
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
