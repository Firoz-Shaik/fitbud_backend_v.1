# tests/unit/test_utils.py
# Unit tests for pure utility functions.

import pytest
from app.domain.client_lifecycle import assert_valid_client_transition, ALLOWED_TRANSITIONS
from app.domain.client_permissions import ACTION_PERMISSIONS
from app.domain.errors import InvalidClientState


class TestClientLifecycleTransitions:
    """Tests for client status transition validation."""
    
    def test_valid_transition_invited_to_active(self):
        """Valid transition from invited to active should not raise error."""
        assert_valid_client_transition("invited", "active")
    
    def test_valid_transition_active_to_paused(self):
        """Valid transition from active to paused should not raise error."""
        assert_valid_client_transition("active", "paused")
    
    def test_valid_transition_active_to_archived(self):
        """Valid transition from active to archived should not raise error."""
        assert_valid_client_transition("active", "archived")
    
    def test_valid_transition_paused_to_active(self):
        """Valid transition from paused to active should not raise error."""
        assert_valid_client_transition("paused", "active")
    
    def test_invalid_transition_invited_to_paused(self):
        """Invalid transition from invited to paused should raise InvalidClientState."""
        with pytest.raises(InvalidClientState, match="Cannot transition"):
            assert_valid_client_transition("invited", "paused")
    
    def test_invalid_transition_archived_to_active(self):
        """Archived clients cannot transition to any state."""
        with pytest.raises(InvalidClientState, match="Cannot transition"):
            assert_valid_client_transition("archived", "active")
    
    def test_invalid_transition_invited_to_archived(self):
        """Cannot directly archive an invited client."""
        with pytest.raises(InvalidClientState, match="Cannot transition"):
            assert_valid_client_transition("invited", "archived")


class TestActionPermissions:
    """Tests for action-based permission matrix."""
    
    def test_checkin_allowed_for_active_clients(self):
        """Checkin action should be allowed for active clients."""
        assert "active" in ACTION_PERMISSIONS["checkin"]
    
    def test_checkin_not_allowed_for_invited_clients(self):
        """Checkin action should not be allowed for invited clients."""
        assert "invited" not in ACTION_PERMISSIONS["checkin"]
    
    def test_assign_workout_only_for_active(self):
        """Workout assignment should only be allowed for active clients."""
        assert ACTION_PERMISSIONS["assign_workout"] == {"active"}
    
    def test_view_logs_allowed_for_active_and_paused(self):
        """View logs should be allowed for active and paused clients."""
        assert "active" in ACTION_PERMISSIONS["view_logs"]
        assert "paused" in ACTION_PERMISSIONS["view_logs"]
    
    def test_delete_client_only_for_invited(self):
        """Delete client should only be allowed for invited status."""
        assert ACTION_PERMISSIONS["delete_client"] == {"invited"}
