"""User service business logic"""
from typing import List

from sqlalchemy.orm import Session

from ..db.models import Team, UserProfile
from ..models.schemas import ProfileUpdate, TeamCreate


class UserService:
    """User management service"""

    @staticmethod
    def get_or_create_profile(db: Session, user_id: str) -> UserProfile:
        """Get or create user profile"""
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        if not profile:
            profile = UserProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)

        return profile

    @staticmethod
    def update_profile(db: Session, user_id: str, profile_data: ProfileUpdate) -> UserProfile:
        """Update user profile"""
        profile = UserService.get_or_create_profile(db, user_id)

        for field, value in profile_data.dict(exclude_unset=True).items():
            setattr(profile, field, value)

        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def create_team(db: Session, user_id: str, team_data: TeamCreate) -> Team:
        """Create a team"""
        team = Team(
            name=team_data.name,
            owner_id=user_id,
            description=team_data.description,
        )

        db.add(team)
        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def get_user_teams(db: Session, user_id: str) -> List[Team]:
        """Get teams owned by user"""
        return db.query(Team).filter(Team.owner_id == user_id).all()
