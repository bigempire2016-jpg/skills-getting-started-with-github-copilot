"""
Tests for signup endpoint functionality.
"""
import pytest


class TestSignupSuccess:
    """Test suite for successful signup scenarios."""
    
    def test_signup_success(self, client, test_email, test_activity_name):
        """
        Test successful signup for an activity.
        
        Arrange: Prepare email and activity name
        Act: Send POST request to signup endpoint
        Assert: Verify 200 response and success message
        """
        # Arrange
        email = "new_student@mergington.edu"
        activity_name = "Basketball Team"  # Empty activity to avoid duplicates
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]
        assert activity_name in response.json()["message"]
    
    def test_signup_multiple_students_same_activity(self, client):
        """
        Test that multiple different students can sign up for the same activity.
        
        Arrange: Prepare two different emails
        Act: Sign up both students to the same activity
        Assert: Verify both signups succeed and get different responses
        """
        # Arrange
        activity_name = "Basketball Team"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in response1.json()["message"]
        assert email2 in response2.json()["message"]


class TestSignupErrors:
    """Test suite for signup error scenarios."""
    
    def test_signup_nonexistent_activity(self, client):
        """
        Test signup to non-existent activity returns 404.
        
        Arrange: Prepare fake activity name
        Act: Send POST request to signup for non-existent activity
        Assert: Verify 404 response and detail message
        """
        # Arrange
        fake_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_email(self, client):
        """
        Test signup with duplicate email returns 400.
        
        Arrange: Activity already has a participant
        Act: Try to sign up same email again
        Assert: Verify 400 response with "already signed up" message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_adds_email_to_participants(self, client):
        """
        Test that signup actually adds email to participants list.
        
        Arrange: Get initial activity data
        Act: Sign up a new student
        Assert: Verify email appears in participants via GET /activities
        """
        # Arrange
        activity_name = "Soccer Club"  # Empty activity
        email = "new_soccer_player@mergington.edu"
        
        # Act - Get initial state
        response_before = client.get("/activities")
        initial_participants = len(response_before.json()[activity_name]["participants"])
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Get final state
        response_after = client.get("/activities")
        final_participants = response_after.json()[activity_name]["participants"]
        
        # Assert
        assert signup_response.status_code == 200
        assert email in final_participants
        assert len(final_participants) == initial_participants + 1


class TestSignupEdgeCases:
    """Test suite for signup edge cases."""
    
    def test_signup_email_case_sensitivity(self, client):
        """
        Test that email comparison is case-insensitive (if implemented).
        
        Arrange: Student is already signed up with lowercase email
        Act: Try to sign up with uppercase version of same email
        Assert: Behavior depends on implementation (test current behavior)
        """
        # Arrange
        activity_name = "Art Club"
        email_lower = "artist@mergington.edu"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_lower}
        )
        
        # Assert first signup succeeds
        assert response1.status_code == 200
    
    def test_signup_with_special_chars_in_email(self, client):
        """
        Test signup with special characters in email (URL encoding).
        
        Arrange: Email with special chars that need URL encoding
        Act: Sign up with URL-encoded email
        Assert: Verify signup succeeds and email is properly stored
        """
        # Arrange
        activity_name = "Drama Club"
        email = "student+test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify email is stored correctly
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
    
    def test_signup_activity_name_case_sensitive(self, client):
        """
        Test that activity name lookup is case-sensitive.
        
        Arrange: Exact activity name is "Chess Club"
        Act: Try to sign up with different case
        Assert: Verify 404 (case-sensitive lookup)
        """
        # Arrange
        email = "player@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/chess%20club/signup",  # lowercase
            params={"email": email}
        )
        
        # Assert - Should fail due to case sensitivity
        assert response.status_code == 404
