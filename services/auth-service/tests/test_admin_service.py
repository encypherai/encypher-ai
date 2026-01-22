"""Tests for admin service helpers."""

from unittest.mock import MagicMock, patch

from app.db.models import Organization, User
from app.services.admin_service import AdminService


def test_update_user_tier_creates_org_when_missing_default_org():
    db = MagicMock()
    user = User(id="user_1", email="test@encypherai.com", default_organization_id=None, is_active=True)
    org = MagicMock(spec=Organization)
    org.id = "org_1"
    org.tier = "starter"

    def query_side_effect(model):
        query = MagicMock()
        if model is Organization:
            query.filter.return_value.first.return_value = None
        elif model is User:
            query.filter.return_value.first.return_value = user
        return query

    db.query.side_effect = query_side_effect

    with patch("app.services.auth_service.AuthService._create_personal_organization", return_value=org):
        result = AdminService.update_user_tier(db=db, user_id=user.id, new_tier="enterprise")

    assert result["success"] is True
    assert user.default_organization_id == org.id
    db.commit.assert_called()
