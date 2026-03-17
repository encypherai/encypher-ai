"""Tests for invitation email dispatch in organization endpoints."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.v1 import organizations as org_api


def test_build_invitation_email_uses_dashboard_invite_route():
    config = org_api.EmailConfig(frontend_url="https://dashboard.encypherai.test", dashboard_url="")

    _, html_content, plain_content = org_api._build_invitation_email(
        config=config,
        recipient_name="Jane Doe",
        inviter_name="Admin User",
        inviter_email="admin@example.com",
        organization_name="Acme Labs",
        role="owner",
        invitation_token="token_123",
        message=None,
        expires_at=None,
        tier="enterprise",
        trial_months=2,
    )

    assert "https://dashboard.encypherai.test/invite/token_123" in html_content
    assert "https://dashboard.encypherai.test/invite/token_123" in plain_content
    assert "You're invited to join Acme Labs" in html_content
    assert "Admin User (admin@example.com)" in html_content
    assert "Accept Invitation" in html_content


@pytest.mark.asyncio
async def test_send_invitation_email_uses_direct_email_sender(monkeypatch):
    config = org_api.EmailConfig(
        frontend_url="https://dashboard.encypherai.test",
        dashboard_url="",
        smtp_host="smtp.example.test",
        smtp_port=587,
        smtp_user="mailer@example.test",
        smtp_pass="not-a-secret",
        smtp_tls=True,
        email_from="noreply@example.test",
        email_from_name="Encypher",
    )
    monkeypatch.setattr(org_api, "_get_email_config", lambda: config)

    to_thread_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(org_api.asyncio, "to_thread", to_thread_mock)

    await org_api._send_invitation_email(
        authorization="Bearer ignored",
        recipient_email="invitee@example.com",
        recipient_name="Jane Doe",
        inviter_name="Admin User",
        inviter_email="admin@example.com",
        organization_name="Acme Labs",
        role="owner",
        invitation_token="token_123",
        message="Welcome!",
        expires_at=None,
        tier="enterprise",
        trial_months=2,
    )

    to_thread_mock.assert_awaited_once()
    args = to_thread_mock.await_args.args
    kwargs = to_thread_mock.await_args.kwargs
    assert args[0] is org_api.send_email
    assert args[1] is config
    assert args[2] == "invitee@example.com"
    assert args[3] == "You're invited to join Acme Labs on Encypher"
    assert "https://dashboard.encypherai.test/invite/token_123" in args[4]
    assert "Accept Invitation" in args[4]
    assert "Admin User (admin@example.com)" in args[4]
    assert "Accept invitation: https://dashboard.encypherai.test/invite/token_123" in args[5]
    assert kwargs == {}


@pytest.mark.asyncio
async def test_send_domain_claim_email_uses_direct_email_sender(monkeypatch):
    config = org_api.EmailConfig(
        frontend_url="https://dashboard.encypherai.test",
        dashboard_url="",
        smtp_host="smtp.example.test",
        smtp_port=587,
        smtp_user="mailer@example.test",
        smtp_pass="not-a-secret",
        smtp_tls=True,
        email_from="noreply@example.test",
        email_from_name="Encypher",
    )
    monkeypatch.setattr(org_api, "_get_email_config", lambda: config)

    to_thread_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(org_api.asyncio, "to_thread", to_thread_mock)

    await org_api._send_domain_claim_email(
        authorization="Bearer ignored",
        recipient_email="admin@example.com",
        organization_name="Acme Labs",
        domain="acme.test",
        email_token="email-token",
        dns_token="dns-token",
    )

    to_thread_mock.assert_awaited_once()
    args = to_thread_mock.await_args.args
    kwargs = to_thread_mock.await_args.kwargs
    assert args[0] is org_api.send_email
    assert args[1] is config
    assert args[2] == "admin@example.com"
    assert args[3] == "Set up DNS verification for acme.test"
    assert "encypher-domain-claim=dns-token" in args[4]
    assert "Optional audit confirmation" in args[5]
    assert kwargs == {}


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

    require_super_admin = MagicMock()
    monkeypatch.setattr(org_api, "require_super_admin", require_super_admin)

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
    require_super_admin.assert_called_once_with(db, inviter.id)
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
async def test_create_enterprise_evaluation_invitation_sends_email(monkeypatch):
    db = MagicMock(spec=Session)
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}

    inviter = MagicMock()
    inviter.id = "user_eval"
    inviter.name = "Admin User"
    inviter.email = "admin@example.com"

    invitation = MagicMock()
    invitation.id = "inv_eval"
    invitation.email = "prospect@example.com"
    invitation.role = "owner"
    invitation.status = "pending"
    invitation.invited_by = inviter.id
    invitation.token = "token_eval"
    invitation.message = None
    invitation.expires_at = datetime.utcnow() + timedelta(days=7)
    invitation.first_name = "Jamie"
    invitation.last_name = "Prospect"
    invitation.organization_name = "Prospect Org"
    invitation.tier = "enterprise"
    invitation.trial_months = 2

    monkeypatch.setattr(org_api, "get_current_user_id", AsyncMock(return_value=inviter.id))

    mock_service = MagicMock()
    mock_service.create_enterprise_evaluation_invitation.return_value = invitation
    monkeypatch.setattr(org_api, "OrganizationService", MagicMock(return_value=mock_service))

    db.query.return_value.filter.return_value.first.return_value = inviter

    require_super_admin = MagicMock()
    monkeypatch.setattr(org_api, "require_super_admin", require_super_admin)

    send_mock = AsyncMock()
    monkeypatch.setattr(org_api, "_send_invitation_email", send_mock)

    payload = org_api.EnterpriseEvaluationInvitationCreate(
        email=invitation.email,
        first_name=invitation.first_name,
        last_name=invitation.last_name,
        organization_name=invitation.organization_name,
    )

    response = await org_api.create_enterprise_evaluation_invitation(payload, request, db)

    assert response["success"] is True
    require_super_admin.assert_called_once_with(db, inviter.id)
    mock_service.create_enterprise_evaluation_invitation.assert_called_once_with(
        organization_name=invitation.organization_name,
        email=invitation.email,
        first_name=invitation.first_name,
        last_name=invitation.last_name,
        inviter_user_id=inviter.id,
    )
    send_mock.assert_awaited_once()
    _, kwargs = send_mock.call_args
    assert kwargs["recipient_email"] == invitation.email
    assert kwargs["recipient_name"] == "Jamie Prospect"
    assert kwargs["organization_name"] == invitation.organization_name
    assert kwargs["tier"] == "enterprise"
    assert kwargs["trial_months"] == 2


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


@pytest.mark.asyncio
async def test_create_domain_claim_succeeds_when_notification_dispatch_fails(monkeypatch):
    db = MagicMock(spec=Session)
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}

    claim = MagicMock()
    claim.id = "odc_123"
    claim.organization_id = "org_123"
    claim.domain = "encypherai.com"
    claim.verification_email = "admin@encypherai.com"
    claim.status = "pending"
    claim.dns_token = "dns-token"
    claim.email_token = "email-token"
    claim.dns_verified_at = None
    claim.email_verified_at = None
    claim.verified_at = None
    claim.auto_join_enabled = False
    claim.created_at = datetime.utcnow()

    org = MagicMock()
    org.name = "Encypher"

    monkeypatch.setattr(org_api, "get_current_user_id", AsyncMock(return_value="user_123"))

    mock_service = MagicMock()
    mock_service.create_domain_claim.return_value = claim
    mock_service.get_organization.return_value = org
    monkeypatch.setattr(org_api, "OrganizationService", MagicMock(return_value=mock_service))

    send_mock = AsyncMock(side_effect=RuntimeError("notification down"))
    monkeypatch.setattr(org_api, "_send_domain_claim_email", send_mock)

    payload = org_api.DomainClaimCreate(domain="encypherai.com", verification_email="admin@encypherai.com")
    response = await org_api.create_domain_claim("org_123", payload, request, db, None)

    assert response["success"] is True
    assert response["data"]["id"] == "odc_123"
    assert response["data"]["dns_txt_record"] == "encypher-domain-claim=dns-token"


@pytest.mark.asyncio
async def test_create_domain_claim_dispatches_verification_email(monkeypatch):
    db = MagicMock(spec=Session)
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}

    claim = MagicMock()
    claim.id = "odc_456"
    claim.organization_id = "org_123"
    claim.domain = "encypherai.com"
    claim.verification_email = "erik.svilich@encypherai.com"
    claim.status = "pending"
    claim.dns_token = "dns-token"
    claim.email_token = "email-token"
    claim.dns_verified_at = None
    claim.email_verified_at = None
    claim.verified_at = None
    claim.auto_join_enabled = False
    claim.created_at = datetime.utcnow()

    org = MagicMock()
    org.name = "Encypher"

    monkeypatch.setattr(org_api, "get_current_user_id", AsyncMock(return_value="user_123"))

    mock_service = MagicMock()
    mock_service.create_domain_claim.return_value = claim
    mock_service.get_organization.return_value = org
    monkeypatch.setattr(org_api, "OrganizationService", MagicMock(return_value=mock_service))

    send_mock = AsyncMock()
    monkeypatch.setattr(org_api, "_send_domain_claim_email", send_mock)

    payload = org_api.DomainClaimCreate(domain="encypherai.com", verification_email="erik.svilich@encypherai.com")
    response = await org_api.create_domain_claim("org_123", payload, request, db, None)

    assert response["success"] is True
    send_mock.assert_awaited_once()
    _, kwargs = send_mock.call_args
    assert kwargs["authorization"] == "Bearer test-token"
    assert kwargs["recipient_email"] == "erik.svilich@encypherai.com"
    assert kwargs["organization_name"] == "Encypher"
    assert kwargs["domain"] == "encypherai.com"
    assert kwargs["email_token"] == "email-token"


@pytest.mark.asyncio
async def test_delete_domain_claim_endpoint_returns_deleted_claim(monkeypatch):
    db = MagicMock(spec=Session)
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}

    claim = MagicMock()
    claim.id = "odc_123"
    claim.organization_id = "org_123"
    claim.domain = "encypherai.com"
    claim.verification_email = "admin@encypherai.com"
    claim.status = "pending"
    claim.dns_token = "dns-token"
    claim.dns_verified_at = None
    claim.email_verified_at = None
    claim.verified_at = None
    claim.auto_join_enabled = False
    claim.created_at = datetime.utcnow()

    monkeypatch.setattr(org_api, "get_current_user_id", AsyncMock(return_value="user_123"))

    mock_service = MagicMock()
    mock_service.delete_domain_claim.return_value = claim
    monkeypatch.setattr(org_api, "OrganizationService", MagicMock(return_value=mock_service))

    response = await org_api.delete_domain_claim("org_123", "odc_123", request, db)

    assert response["success"] is True
    assert response["data"]["id"] == "odc_123"
    mock_service.delete_domain_claim.assert_called_once_with("org_123", "odc_123", "user_123")


@pytest.mark.asyncio
async def test_update_publisher_settings_requires_verified_domain_for_org_account(monkeypatch):
    db = MagicMock(spec=Session)
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}

    org = MagicMock()
    org.id = "org_123"
    org.account_type = "organization"
    org.display_name = None
    org.name = "Encypher"
    org.anonymous_publisher = False

    monkeypatch.setattr(org_api, "get_current_user_id", AsyncMock(return_value="user_123"))

    mock_service = MagicMock()
    mock_service._has_permission.return_value = True
    mock_service.get_organization.return_value = org
    monkeypatch.setattr(org_api, "OrganizationService", MagicMock(return_value=mock_service))

    db.query.return_value.filter.return_value.first.return_value = None

    payload = org_api.PublisherSettingsUpdate(display_name="Encypher AI")
    with pytest.raises(HTTPException) as exc_info:
        await org_api.update_publisher_settings("org_123", payload, request, db)

    assert exc_info.value.status_code == 400
    assert "Verify at least one organization domain" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_update_publisher_settings_allows_verified_domain_for_org_account(monkeypatch):
    db = MagicMock(spec=Session)
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}

    org = MagicMock()
    org.id = "org_123"
    org.account_type = "organization"
    org.display_name = None
    org.name = "Encypher"
    org.anonymous_publisher = False

    verified_claim = MagicMock()
    verified_claim.id = "odc_verified"

    monkeypatch.setattr(org_api, "get_current_user_id", AsyncMock(return_value="user_123"))

    mock_service = MagicMock()
    mock_service._has_permission.return_value = True
    mock_service.get_organization.return_value = org
    monkeypatch.setattr(org_api, "OrganizationService", MagicMock(return_value=mock_service))

    db.query.return_value.filter.return_value.first.return_value = verified_claim

    payload = org_api.PublisherSettingsUpdate(display_name="Encypher AI")
    response = await org_api.update_publisher_settings("org_123", payload, request, db)

    assert response["success"] is True
    assert response["data"]["display_name"] == "Encypher AI"


@pytest.mark.asyncio
async def test_update_publisher_settings_custom_mode_requires_add_on(monkeypatch):
    db = MagicMock(spec=Session)
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}

    org = MagicMock()
    org.id = "org_123"
    org.account_type = "organization"
    org.display_name = "Encypher"
    org.name = "Encypher"
    org.anonymous_publisher = False
    org.tier = "free"
    org.add_ons = {}

    verified_claim = MagicMock()
    verified_claim.id = "odc_verified"

    monkeypatch.setattr(org_api, "get_current_user_id", AsyncMock(return_value="user_123"))

    mock_service = MagicMock()
    mock_service._has_permission.return_value = True
    mock_service.get_organization.return_value = org
    monkeypatch.setattr(org_api, "OrganizationService", MagicMock(return_value=mock_service))

    db.query.return_value.filter.return_value.first.return_value = verified_claim

    payload = org_api.PublisherSettingsUpdate(
        display_name="Encypher Editorial",
        signing_identity_mode="custom",
    )
    with pytest.raises(HTTPException) as exc_info:
        await org_api.update_publisher_settings("org_123", payload, request, db)

    assert exc_info.value.status_code == 400
    assert "Custom signing identity requires" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_update_publisher_settings_returns_signing_identity_mode_fields(monkeypatch):
    db = MagicMock(spec=Session)
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test-token"}

    org = MagicMock()
    org.id = "org_123"
    org.account_type = "organization"
    org.display_name = "Encypher"
    org.name = "Encypher"
    org.anonymous_publisher = False
    org.tier = "free"
    org.add_ons = {"custom-signing-identity": {"enabled": True}}
    org.signing_identity_mode = "organization_name"
    org.signing_identity_custom_label = None

    verified_claim = MagicMock()
    verified_claim.id = "odc_verified"

    monkeypatch.setattr(org_api, "get_current_user_id", AsyncMock(return_value="user_123"))

    mock_service = MagicMock()
    mock_service._has_permission.return_value = True
    mock_service.get_organization.return_value = org
    monkeypatch.setattr(org_api, "OrganizationService", MagicMock(return_value=mock_service))

    db.query.return_value.filter.return_value.first.return_value = verified_claim

    payload = org_api.PublisherSettingsUpdate(signing_identity_mode="custom", display_name="Encypher Editorial")
    response = await org_api.update_publisher_settings("org_123", payload, request, db)

    assert response["success"] is True
    assert response["data"]["signing_identity_mode"] == "custom"
    assert response["data"]["signing_identity_custom_label"] == "Encypher Editorial"
