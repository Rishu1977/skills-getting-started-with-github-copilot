"""
Unit tests for business logic.
Tests validation logic and data integrity rules.
"""

import pytest


class TestParticipantValidation:
    """Tests for participant list validation logic."""
    
    def test_participant_list_is_case_sensitive(self, fresh_activities):
        """Email addresses are stored and compared as-is (case sensitive)."""
        activities = fresh_activities
        
        # Alice@test.edu is different from alice@test.edu
        assert "alice@test.edu" in activities["Chess Club"]["participants"]
        assert "Alice@test.edu" not in activities["Chess Club"]["participants"]
    
    def test_participant_list_preserves_order(self, fresh_activities):
        """Participants are stored in insertion order."""
        activities = fresh_activities
        
        # Add new participants
        activities["Gym Class"]["participants"].append("diana@test.edu")
        activities["Gym Class"]["participants"].append("eve@test.edu")
        
        participants = activities["Gym Class"]["participants"]
        assert participants[0] == "diana@test.edu"
        assert participants[1] == "eve@test.edu"
    
    def test_empty_activity_has_no_participants(self, fresh_activities):
        """Activities can have zero participants."""
        activities = fresh_activities
        
        gym_participants = activities["Gym Class"]["participants"]
        assert len(gym_participants) == 0
        assert gym_participants == []
    
    def test_participant_list_allows_duplicates_if_not_checked(self, fresh_activities):
        """
        The participant list can theoretically have duplicates if validation isn't enforced.
        This test documents the vulnerability that the endpoint check prevents.
        """
        activities = fresh_activities
        
        # Direct list manipulation (bypassing endpoint validation)
        activities["Chess Club"]["participants"].append("alice@test.edu")
        
        # Now alice appears twice (endpoint validation should prevent this)
        count = activities["Chess Club"]["participants"].count("alice@test.edu")
        assert count == 2
