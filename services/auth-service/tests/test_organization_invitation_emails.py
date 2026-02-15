"""Tests for invitation email dispatch in organization endpoints."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.orm import Session

from app.api.v1 import organizations as org_api


@pytest.mark.asyncio
async def test_create_invitation_sends_email(monkeypatch):
    db = MagicMock(spec=Session)
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}

    inviter = MagicMock()
    inviter.id = "user_123"
    inviter.name = "Inviter Name"
    inviter.email = "inviter@example.com"

    invitation = MagicMock()
    invitation.id = "inv_123"
    invitation.email = "invitee@example.com"
    invitation.role = "member"
    invitation.status = "pending"
    invitation.invited_by = inviter.id
    invitation.token = "token_123"
    invitation.message = "Welcome!"
    invitation.expires_at = datetime.utcnow() + timedelta(days=7)
    invitation.first_name = "Jane"
    invitation.last_name = "Doe"
    invitation.organization_name = "Acme Labs"
    invitation.tier = "business"
    invitation.trial_months = 3

    org = MagicMock()
    org.name = "Acme"

    monkeypatch.setattr(org_api, "get_current_user_id", AsyncMock(return_value=inviter.id))

    mock_service = MagicMock()
    mock_service.create_invitation.return_value = invitation
    mock_service.get_organization.return_value = org
    monkeypatch.setattr(org_api, "OrganizationService", MagicMock(return_value=mock_service))

    db.query.return_value.filter.return_value.first.return_value = inviter

    send_mock = AsyncMock()
    monkeypatch.setattr(org_api, "_send_invitation_email", send_mock)

    payload = org_api.InvitationCreate(
        email=invitation.email,
        role=invitation.role,
        message=invitation.message,
        first_name=invitation.first_name,
        last_name=invitation.last_name,
        organization_name=invitation.organization_name,
        tier=org_api.UserTier.ENTERPRISE,
        trial_months=invitation.trial_months,
    )

    response = await org_api.create_invitation("org_123", payload, request, db)

    assert response["success"] is True
    mock_service.create_invitation.assert_called_once_with(
        org_id="org_123",
        email=invitation.email,
        role=invitation.role,
        inviter_user_id=inviter.id,
        message=invitation.message,
        first_name=invitation.first_name,
        last_name=invitation.last_name,
        organization_name=invitation.organization_name,
        tier=org_api.UserTier.ENTERPRISE.value,
        trial_months=invitation.trial_months,
    )
    send_mock.assert_awaited_once()
    _, kwargs = send_mock.call_args
    assert kwargs["authorization"] == "Bearer test-token"
    assert kwargs["recipient_email"] == invitation.email
    assert kwargs["recipient_name"] == "Jane Doe"
    assert kwargs["inviter_name"] == inviter.name
    assert kwargs["inviter_email"] == inviter.email
    assert kwargs["organization_name"] == invitation.organization_name
    assert kwargs["role"] == invitation.role
    assert kwargs["invitation_token"] == invitation.token
    assert kwargs["message"] == invitation.message
    assert kwargs["expires_at"] == invitation.expires_at
    assert kwargs["tier"] == invitation.tier
    assert kwargs["trial_months"] == invitation.trial_months


@pytest.mark.asyncio
async def test_trial_invitation_requires_super_admin(monkeypatch):
    db = MagicMock(spec=Session)
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}

    inviter = MagicMock()
    inviter.id = "user_123"
    inviter.name = "Inviter Name"
    inviter.email = "inviter@example.com"

    invitation = MagicMock()
    invitation.id = "inv_789"
    invitation.email = "invitee@example.com"
    invitation.role = "member"
    invitation.status = "pending"
    invitation.invited_by = inviter.id
    invitation.token = "token_789"
    invitation.message = None
    invitation.expires_at = datetime.utcnow() + timedelta(days=7)
    invitation.first_name = "Jane"
    invitation.last_name = "Doe"
    invitation.organization_name = "Acme Labs"
    invitation.tier = "business"
    invitation.trial_months = 2

    monkeypatch.setattr(org_api, "get_current_user_id", AsyncMock(return_value=inviter.id))

    mock_service = MagicMock()
    mock_service.create_invitation.return_value = invitation
    mock_service.get_organization.return_value = MagicMock(name="Acme")
    monkeypatch.setattr(org_api, "OrganizationService", MagicMock(return_value=mock_service))

    db.query.return_value.filter.return_value.first.return_value = inviter

    require_super_admin = MagicMock()
    monkeypatch.setattr(org_api, "require_super_admin", require_super_admin)
    monkeypatch.setattr(org_api, "_send_invitation_email", AsyncMock())

    payload = org_api.InvitationCreate(
        email=invitation.email,
        role=invitation.role,
        message=invitation.message,
        organization_name=invitation.organization_name,
        tier=org_api.UserTier.ENTERPRISE,
        trial_months=invitation.trial_months,
    )

    response = await org_api.create_invitation("org_123", payload, request, db)

    assert response["success"] is True
    require_super_admin.assert_called_once_with(db, inviter.id)


@pytest.mark.asyncio
async def test_create_trial_invitation_for_new_org_sends_email(monkeypatch):
    db = MagicMock(spec=Session)
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}

    inviter = MagicMock()
    inviter.id = "user_456"
    inviter.name = "Admin User"
    inviter.email = "admin@example.com"

    invitation = MagicMock()
    invitation.id = "inv_999"
    invitation.email = "invitee@example.com"
    invitation.role = "owner"
    invitation.status = "pending"
    invitation.invited_by = inviter.id
    invitation.token = "token_999"
    invitation.message = None
    invitation.expires_at = datetime.utcnow() + timedelta(days=7)
    invitation.first_name = "Jane"
    invitation.last_name = "Doe"
    invitation.organization_name = "New Org"
    invitation.tier = "business"
    invitation.trial_months = 3

    monkeypatch.setattr(org_api, "get_current_user_id", AsyncMock(return_value=inviter.id))

    mock_service = MagicMock()
    mock_service.create_trial_invitation_for_new_org.return_value = invitation
    monkeypatch.setattr(org_api, "OrganizationService", MagicMock(return_value=mock_service))

    db.query.return_value.filter.return_value.first.return_value = inviter

    require_super_admin = MagicMock()
    monkeypatch.setattr(org_api, "require_super_admin", require_super_admin)

    send_mock = AsyncMock()
    monkeypatch.setattr(org_api, "_send_invitation_email", send_mock)

    payload = org_api.TrialInvitationCreate(
        email=invitation.email,
        first_name=invitation.first_name,
        last_name=invitation.last_name,
        organization_name=invitation.organization_name,
        tier=org_api.UserTier.ENTERPRISE,
        trial_months=invitation.trial_months,
    )

    response = await org_api.create_trial_invitation_for_new_org(payload, request, db)

    assert response["success"] is True
    require_super_admin.assert_called_once_with(db, inviter.id)
    mock_service.create_trial_invitation_for_new_org.assert_called_once_with(
        organization_name=invitation.organization_name,
        email=invitation.email,
        first_name=invitation.first_name,
        last_name=invitation.last_name,
        tier=org_api.UserTier.ENTERPRISE.value,
        trial_months=invitation.trial_months,
        inviter_user_id=inviter.id,
    )
    send_mock.assert_awaited_once()
    _, kwargs = send_mock.call_args
    assert kwargs["recipient_email"] == invitation.email
    assert kwargs["recipient_name"] == "Jane Doe"
    assert kwargs["organization_name"] == invitation.organization_name


@pytest.mark.asyncio
async def test_resend_invitation_sends_email(monkeypatch):
    db = MagicMock(spec=Session)
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}

    inviter = MagicMock()
    inviter.id = "user_123"
    inviter.name = "Inviter Name"
    inviter.email = "inviter@example.com"

    invitation = MagicMock()
    invitation.id = "inv_456"
    invitation.email = "invitee@example.com"
    invitation.role = "manager"
    invitation.status = "pending"
    invitation.invited_by = inviter.id
    invitation.token = "token_456"
    invitation.message = None
    invitation.expires_at = datetime.utcnow() + timedelta(days=7)
    invitation.first_name = "Jane"
    invitation.last_name = "Doe"
    invitation.organization_name = "Acme Labs"
    invitation.tier = "business"
    invitation.trial_months = 6

    org = MagicMock()
    org.name = "Acme"

    monkeypatch.setattr(org_api, "get_current_user_id", AsyncMock(return_value=inviter.id))

    mock_service = MagicMock()
    mock_service.resend_invitation.return_value = invitation
    mock_service.get_organization.return_value = org
    monkeypatch.setattr(org_api, "OrganizationService", MagicMock(return_value=mock_service))

    db.query.return_value.filter.return_value.first.return_value = inviter

    send_mock = AsyncMock()
    monkeypatch.setattr(org_api, "_send_invitation_email", send_mock)

    response = await org_api.resend_invitation("org_123", "inv_123", request, db)

    assert response["success"] is True
    send_mock.assert_awaited_once()
    _, kwargs = send_mock.call_args
    assert kwargs["role"] == invitation.role
    assert kwargs["invitation_token"] == invitation.token
    assert kwargs["recipient_email"] == invitation.email
    assert kwargs["recipient_name"] == "Jane Doe"
    assert kwargs["organization_name"] == invitation.organization_name
    assert kwargs["tier"] == invitation.tier
    assert kwargs["trial_months"] == invitation.trial_months
