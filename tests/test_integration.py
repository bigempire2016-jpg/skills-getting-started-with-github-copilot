"""
Integration tests for multi-step workflows.
"""
import pytest


class TestSignupUnregisterWorkflows:
    """Test suite for signup/unregister integration workflows."""
    
    def test_full_signup_unregister_cycle(self, client):
        """
        Test complete cycle: signup -> verify -> unregister -> verify.
        
        Arrange: Prepare test data
        Act: Sign up, check participants, unregister, check participants again
        Assert: Verify state changes at each step
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "new_player@mergington.edu"
        
        # Act - Get initial state
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Signup successful
        assert signup_response.status_code == 200
        
        # Act - Check participants after signup
        after_signup = client.get("/activities")
        after_signup_count = len(after_signup.json()[activity_name]["participants"])
        
        # Assert - Participant count increased
        assert after_signup_count == initial_count + 1
        assert email in after_signup.json()[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert - Unregister successful
        assert unregister_response.status_code == 200
        
        # Act - Check participants after unregister
        after_unregister = client.get("/activities")
        after_unregister_count = len(after_unregister.json()[activity_name]["participants"])
        
        # Assert - Participant count returned to initial
        assert after_unregister_count == initial_count
        assert email not in after_unregister.json()[activity_name]["participants"]
    
    def test_multiple_signups_and_unregisters(self, client):
        """
        Test multiple students signing up and unregistering.
        
        Arrange: Prepare multiple emails
        Act: Sign up multiple students, unregister some, verify state
        Assert: Verify participants list is correct at each step
        """
        # Arrange
        activity_name = "Soccer Club"
        student1 = "soccer_player1@mergington.edu"
        student2 = "soccer_player2@mergington.edu"
        student3 = "soccer_player3@mergington.edu"
        
        # Act - Get initial state
        initial = client.get("/activities").json()[activity_name]["participants"]
        
        # Act - Sign up three students
        client.post(f"/activities/{activity_name}/signup", params={"email": student1})
        client.post(f"/activities/{activity_name}/signup", params={"email": student2})
        client.post(f"/activities/{activity_name}/signup", params={"email": student3})
        
        # Act - Check state after all signups
        after_signups = client.get("/activities").json()[activity_name]["participants"]
        
        # Assert - All three added
        assert len(after_signups) == len(initial) + 3
        assert student1 in after_signups
        assert student2 in after_signups
        assert student3 in after_signups
        
        # Act - Unregister one
        client.delete(f"/activities/{activity_name}/unregister", params={"email": student2})
        
        # Assert - One removed, two remain
        after_one_unregister = client.get("/activities").json()[activity_name]["participants"]
        assert len(after_one_unregister) == len(initial) + 2
        assert student1 in after_one_unregister
        assert student2 not in after_one_unregister
        assert student3 in after_one_unregister


class TestAvailabilityTracking:
    """Test suite for tracking activity availability."""
    
    def test_signup_decreases_availability(self, client):
        """
        Test that signing up decreases available spots.
        
        Arrange: Get activity with available spots
        Act: Sign up a student
        Assert: Verify available spots decreased by 1
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "player@mergington.edu"
        
        # Act - Get initial availability
        initial = client.get("/activities").json()[activity_name]
        initial_spots = initial["max_participants"] - len(initial["participants"])
        
        # Act - Sign up
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert - Check availability
        after = client.get("/activities").json()[activity_name]
        after_spots = after["max_participants"] - len(after["participants"])
        
        assert after_spots == initial_spots - 1
    
    def test_unregister_increases_availability(self, client):
        """
        Test that unregistering increases available spots.
        
        Arrange: Get activity with participants
        Act: Unregister a student
        Assert: Verify available spots increased by 1
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act - Get initial availability
        initial = client.get("/activities").json()[activity_name]
        initial_spots = initial["max_participants"] - len(initial["participants"])
        
        # Act - Unregister
        client.delete(f"/activities/{activity_name}/unregister", params={"email": email_to_remove})
        
        # Assert - Check availability
        after = client.get("/activities").json()[activity_name]
        after_spots = after["max_participants"] - len(after["participants"])
        
        assert after_spots == initial_spots + 1
    
    def test_availability_consistent_across_activities(self, client):
        """
        Test that signup/unregister in one activity doesn't affect others.
        
        Arrange: Get initial state of two activities
        Act: Sign up for one activity
        Assert: Verify only that activity's availability changed
        """
        # Arrange
        activity1 = "Chess Club"
        activity2 = "Basketball Team"
        email = "multi_activity_player@mergington.edu"
        
        # Act - Get initial state
        initial_state = client.get("/activities").json()
        chess_initial_params = len(initial_state[activity1]["participants"])
        basketball_initial_params = len(initial_state[activity2]["participants"])
        
        # Act - Sign up for Basketball only
        client.post(f"/activities/{activity2}/signup", params={"email": email})
        
        # Assert - Check final state
        final_state = client.get("/activities").json()
        
        # Chess should be unchanged
        assert len(final_state[activity1]["participants"]) == chess_initial_params
        
        # Basketball should have one more
        assert len(final_state[activity2]["participants"]) == basketball_initial_params + 1
        assert email in final_state[activity2]["participants"]


class TestDataIntegrity:
    """Test suite for data integrity across operations."""
    
    def test_participant_data_integrity_after_operations(self, client):
        """
        Test that participant data remains consistent after operations.
        
        Arrange: Track original participants
        Act: Sign up new student, unregister, sign up again
        Assert: Verify data is consistent and no corruption
        """
        # Arrange
        activity_name = "Programming Class"
        original_participants = client.get("/activities").json()[activity_name]["participants"][:]
        new_student = "programmer@mergington.edu"
        
        # Act - Sign up
        client.post(f"/activities/{activity_name}/signup", params={"email": new_student})
        
        # Assert - Original participants still there
        after_signup = client.get("/activities").json()[activity_name]["participants"]
        for original in original_participants:
            assert original in after_signup
        assert new_student in after_signup
        
        # Act - Unregister
        client.delete(f"/activities/{activity_name}/unregister", params={"email": new_student})
        
        # Assert - Back to original state
        after_unregister = client.get("/activities").json()[activity_name]["participants"]
        assert sorted(after_unregister) == sorted(original_participants)
    
    def test_other_activity_fields_unchanged_after_signup(self, client):
        """
        Test that signup doesn't modify other fields (description, schedule, etc).
        
        Arrange: Get initial activity data
        Act: Sign up a student
        Assert: Verify non-participant fields are unchanged
        """
        # Arrange
        activity_name = "Debate Club"
        initial = client.get("/activities").json()[activity_name]
        initial_description = initial["description"]
        initial_schedule = initial["schedule"]
        initial_max = initial["max_participants"]
        
        email = "debater@mergington.edu"
        
        # Act - Sign up
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert - Other fields unchanged
        after = client.get("/activities").json()[activity_name]
        assert after["description"] == initial_description
        assert after["schedule"] == initial_schedule
        assert after["max_participants"] == initial_max
