"""
Integration tests for FastAPI endpoints.
Tests the POST /signup and DELETE /unregister endpoints via HTTP.
"""

import pytest


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup"""
    
    def test_signup_valid_student(self, client_with_fresh_activities):
        """Happy path: A new student can sign up for an activity."""
        response = client_with_fresh_activities.post(
            "/activities/Chess Club/signup?email=diana@test.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up diana@test.edu for Chess Club" in data["message"]
    
    def test_signup_updates_participant_list(self, client_with_fresh_activities):
        """Verify that a signed-up student appears in the participants list."""
        # Sign up new student
        client_with_fresh_activities.post(
            "/activities/Chess Club/signup?email=diana@test.edu"
        )
        
        # Fetch activities to verify participant was added
        response = client_with_fresh_activities.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        
        assert "diana@test.edu" in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 3  # alice, bob, diana
    
    def test_signup_invalid_activity(self, client_with_fresh_activities):
        """Error: Attempting to sign up for a non-existent activity returns 404."""
        response = client_with_fresh_activities.post(
            "/activities/Nonexistent Club/signup?email=diana@test.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_email(self, client_with_fresh_activities):
        """Error: A student cannot sign up twice for the same activity."""
        # Try to sign up alice (already in Chess Club) again
        response = client_with_fresh_activities.post(
            "/activities/Chess Club/signup?email=alice@test.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students_same_activity(self, client_with_fresh_activities):
        """Multiple different students can sign up for the same activity."""
        # Add first student
        response1 = client_with_fresh_activities.post(
            "/activities/Gym Class/signup?email=diana@test.edu"
        )
        assert response1.status_code == 200
        
        # Add second student
        response2 = client_with_fresh_activities.post(
            "/activities/Gym Class/signup?email=eve@test.edu"
        )
        assert response2.status_code == 200
        
        # Verify both are in the list
        response = client_with_fresh_activities.get("/activities")
        participants = response.json()["Gym Class"]["participants"]
        assert "diana@test.edu" in participants
        assert "eve@test.edu" in participants
    
    def test_signup_same_student_different_activities(self, client_with_fresh_activities):
        """A student can sign up for multiple different activities."""
        # Diana signs up for Chess Club
        response1 = client_with_fresh_activities.post(
            "/activities/Chess Club/signup?email=diana@test.edu"
        )
        assert response1.status_code == 200
        
        # Diana signs up for Gym Class
        response2 = client_with_fresh_activities.post(
            "/activities/Gym Class/signup?email=diana@test.edu"
        )
        assert response2.status_code == 200
        
        # Verify Diana is in both activities
        response = client_with_fresh_activities.get("/activities")
        assert "diana@test.edu" in response.json()["Chess Club"]["participants"]
        assert "diana@test.edu" in response.json()["Gym Class"]["participants"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister"""
    
    def test_unregister_valid_student(self, client_with_fresh_activities):
        """Happy path: A registered student can unregister from an activity."""
        response = client_with_fresh_activities.delete(
            "/activities/Chess Club/unregister?email=alice@test.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered alice@test.edu from Chess Club" in data["message"]
    
    def test_unregister_removes_from_participant_list(self, client_with_fresh_activities):
        """Verify that unregistered student is removed from participants list."""
        # Unregister alice
        client_with_fresh_activities.delete(
            "/activities/Chess Club/unregister?email=alice@test.edu"
        )
        
        # Fetch activities to verify participant was removed
        response = client_with_fresh_activities.get("/activities")
        activities = response.json()
        
        assert "alice@test.edu" not in activities["Chess Club"]["participants"]
        assert "bob@test.edu" in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 1  # Only bob left
    
    def test_unregister_invalid_activity(self, client_with_fresh_activities):
        """Error: Attempting to unregister from non-existent activity returns 404."""
        response = client_with_fresh_activities.delete(
            "/activities/Nonexistent Club/unregister?email=alice@test.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_student_not_registered(self, client_with_fresh_activities):
        """Error: Cannot unregister a student who is not registered."""
        response = client_with_fresh_activities.delete(
            "/activities/Chess Club/unregister?email=notregistered@test.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_already_unregistered_student(self, client_with_fresh_activities):
        """Error: Cannot unregister the same student twice."""
        # First unregister alice (succeeds)
        response1 = client_with_fresh_activities.delete(
            "/activities/Chess Club/unregister?email=alice@test.edu"
        )
        assert response1.status_code == 200
        
        # Try to unregister alice again (should fail)
        response2 = client_with_fresh_activities.delete(
            "/activities/Chess Club/unregister?email=alice@test.edu"
        )
        assert response2.status_code == 400
        assert "not registered" in response2.json()["detail"]
    
    def test_unregister_all_participants(self, client_with_fresh_activities):
        """All participants can be unregistered from an activity."""
        # Unregister alice
        client_with_fresh_activities.delete(
            "/activities/Chess Club/unregister?email=alice@test.edu"
        )
        
        # Unregister bob
        client_with_fresh_activities.delete(
            "/activities/Chess Club/unregister?email=bob@test.edu"
        )
        
        # Verify activity has no participants
        response = client_with_fresh_activities.get("/activities")
        assert len(response.json()["Chess Club"]["participants"]) == 0


class TestSignupUnregisterWorkflow:
    """Integration tests combining signup and unregister operations."""
    
    def test_signup_then_unregister(self, client_with_fresh_activities):
        """Complete workflow: register a student, then unregister them."""
        # Sign up diana
        response1 = client_with_fresh_activities.post(
            "/activities/Gym Class/signup?email=diana@test.edu"
        )
        assert response1.status_code == 200
        
        # Verify diana is registered
        response = client_with_fresh_activities.get("/activities")
        assert "diana@test.edu" in response.json()["Gym Class"]["participants"]
        
        # Unregister diana
        response2 = client_with_fresh_activities.delete(
            "/activities/Gym Class/unregister?email=diana@test.edu"
        )
        assert response2.status_code == 200
        
        # Verify diana is no longer registered
        response = client_with_fresh_activities.get("/activities")
        assert "diana@test.edu" not in response.json()["Gym Class"]["participants"]
    
    def test_signup_unregister_signup_again(self, client_with_fresh_activities):
        """A student can re-register after unregistering."""
        # Sign up diana
        client_with_fresh_activities.post(
            "/activities/Gym Class/signup?email=diana@test.edu"
        )
        
        # Unregister diana
        client_with_fresh_activities.delete(
            "/activities/Gym Class/unregister?email=diana@test.edu"
        )
        
        # Re-register diana (should succeed)
        response = client_with_fresh_activities.post(
            "/activities/Gym Class/signup?email=diana@test.edu"
        )
        assert response.status_code == 200
        
        # Verify diana is back
        response_get = client_with_fresh_activities.get("/activities")
        assert "diana@test.edu" in response_get.json()["Gym Class"]["participants"]
