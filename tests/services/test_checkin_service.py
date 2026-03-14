# tests/services/test_checkin_service.py
# Service layer tests for check-in business logic.

import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.checkin_service import checkin_service
from app.schemas.checkin import CheckinCreate
from app.models.user import User
from app.models.client import Client
from app.models.activity import ActivityFeed
from app.domain.errors import InvalidClientState


class TestCheckinCreation:
    """Tests for creating check-ins."""
    
    def test_client_creates_checkin_linked_correctly(self, test_db: Session, test_client_user: User, test_client_profile: Client):
        """Client should be able to create a check-in linked to their profile."""
        checkin_data = CheckinCreate(
            weight_kg=75.5,
            notes="Feeling great this week!"
        )
        
        checkin = checkin_service.create_checkin(
            db=test_db,
            obj_in=checkin_data,
            current_client=test_client_user
        )
        
        assert checkin.client_id == test_client_profile.id
        assert checkin.weight_kg == 75.5
        assert checkin.notes == "Feeling great this week!"
    
    def test_checkin_creates_activity_feed_entry(self, test_db: Session, test_client_user: User, test_client_profile: Client):
        """Creating a check-in should also create an activity feed entry."""
        checkin_data = CheckinCreate(
            weight_kg=80.0,
            notes="Weekly check-in"
        )
        
        checkin = checkin_service.create_checkin(
            db=test_db,
            obj_in=checkin_data,
            current_client=test_client_user
        )
        
        # Verify activity feed entry was created
        activity = test_db.query(ActivityFeed).filter(
            ActivityFeed.client_id == test_client_profile.id,
            ActivityFeed.event_type == "CHECKIN_SUBMITTED"
        ).first()
        
        assert activity is not None
        assert activity.event_metadata.get("weight") == "80.0 kg"
    
    def test_checkin_without_weight_creates_activity(self, test_db: Session, test_client_user: User, test_client_profile: Client):
        """Check-in without weight should still create activity feed entry."""
        checkin_data = CheckinCreate(
            notes="Just checking in"
        )
        
        checkin = checkin_service.create_checkin(
            db=test_db,
            obj_in=checkin_data,
            current_client=test_client_user
        )
        
        activity = test_db.query(ActivityFeed).filter(
            ActivityFeed.client_id == test_client_profile.id,
            ActivityFeed.event_type == "CHECKIN_SUBMITTED"
        ).first()
        
        assert activity is not None
        assert "weight" not in activity.event_metadata


class TestCheckinPermissions:
    """Tests for check-in permission enforcement."""
    
    def test_invited_client_cannot_checkin(self, test_db: Session, test_trainer: User):
        """Invited clients should not be able to check in."""
        from app.services.client_service import client_service
        from app.schemas.client import ClientInvite
        
        # Create invited client
        invite_data = ClientInvite(email="invited@test.com", full_name="Invited Client", goal="Weight Loss")
        invited_client = client_service.create_client_invite(db=test_db, obj_in=invite_data, trainer_id=test_trainer.id)
        
        # Create a user for the invited client (but status is still invited)
        invited_user = User(
            email="invited@test.com",
            hashed_password="hash",
            full_name="Invited Client",
            user_role="client"
        )
        test_db.add(invited_user)
        test_db.commit()
        
        invited_client.client_user_id = invited_user.id
        test_db.commit()
        test_db.refresh(invited_user)
        
        checkin_data = CheckinCreate(weight_kg=70.0, notes="Test")
        
        with pytest.raises(InvalidClientState, match="not allowed when client is 'invited'"):
            checkin_service.create_checkin(
                db=test_db,
                obj_in=checkin_data,
                current_client=invited_user
            )
    
    def test_active_client_can_checkin(self, test_db: Session, test_client_user: User, test_client_profile: Client):
        """Active clients should be able to check in."""
        checkin_data = CheckinCreate(weight_kg=75.0, notes="Active check-in")
        
        checkin = checkin_service.create_checkin(
            db=test_db,
            obj_in=checkin_data,
            current_client=test_client_user
        )
        
        assert checkin is not None
        assert checkin.client_id == test_client_profile.id


class TestCheckinRetrieval:
    """Tests for retrieving check-ins."""
    
    def test_get_checkins_by_client(self, test_db: Session, test_client_user: User, test_client_profile: Client):
        """Should retrieve check-ins for a specific client."""
        # Create multiple check-ins
        for i in range(3):
            checkin_data = CheckinCreate(weight_kg=75.0 + i, notes=f"Check-in {i}")
            checkin_service.create_checkin(db=test_db, obj_in=checkin_data, current_client=test_client_user)
        
        checkins = checkin_service.get_checkins_by_client(
            db=test_db,
            client_id=test_client_profile.id,
            current_user=test_client_user,
            start_date=None,
            end_date=None,
            skip=0,
            limit=10
        )
        
        assert len(checkins) == 3
    
    def test_trainer_can_view_client_checkins(self, test_db: Session, test_trainer: User, test_client_user: User, test_client_profile: Client):
        """Trainer should be able to view their client's check-ins."""
        checkin_data = CheckinCreate(weight_kg=75.0, notes="Test")
        checkin_service.create_checkin(db=test_db, obj_in=checkin_data, current_client=test_client_user)
        
        checkins = checkin_service.get_checkins_by_client(
            db=test_db,
            client_id=test_client_profile.id,
            current_user=test_trainer,
            start_date=None,
            end_date=None,
            skip=0,
            limit=10
        )
        
        assert len(checkins) == 1
    
    def test_client_cannot_view_other_client_checkins(self, test_db: Session, test_trainer: User, test_client_user: User):
        """Client should not be able to view another client's check-ins."""
        from app.domain.errors import OwnershipViolation
        import uuid
        
        # Create another client
        other_client_user = User(
            id=uuid.uuid4(),
            email="other@client.com",
            hashed_password="hash",
            full_name="Other Client",
            user_role="client"
        )
        test_db.add(other_client_user)
        test_db.commit()
        
        other_client_profile = Client(
            id=uuid.uuid4(),
            trainer_user_id=test_trainer.id,
            client_user_id=other_client_user.id,
            client_status="active"
        )
        test_db.add(other_client_profile)
        test_db.commit()
        
        with pytest.raises(OwnershipViolation):
            checkin_service.get_checkins_by_client(
                db=test_db,
                client_id=other_client_profile.id,
                current_user=test_client_user,
                start_date=None,
                end_date=None,
                skip=0,
                limit=10
            )
