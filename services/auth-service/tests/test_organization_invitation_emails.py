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

    payload = org_api.InvitationCreate(email=invitation.email, role=invitation.role, message=invitation.message)

    response = await org_api.create_invitation("org_123", payload, request, db)

    assert response["success"] is True
    send_mock.assert_awaited_once()
    _, kwargs = send_mock.call_args
    assert kwargs["authorization"] == "Bearer test-token"
    assert kwargs["recipient_email"] == invitation.email
    assert kwargs["inviter_name"] == inviter.name
    assert kwargs["inviter_email"] == inviter.email
    assert kwargs["organization_name"] == org.name
    assert kwargs["role"] == invitation.role
    assert kwargs["invitation_token"] == invitation.token
    assert kwargs["message"] == invitation.message
    assert kwargs["expires_at"] == invitation.expires_at


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
