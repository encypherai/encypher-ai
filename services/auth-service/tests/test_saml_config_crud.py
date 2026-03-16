"""Tests for SAML SSO config CRUD and ACS endpoint (TEAM_257)."""

import base64
import uuid

import pytest
from unittest.mock import MagicMock, patch


def _mock_admin_auth():
    """Patch _require_authenticated_org_admin to bypass auth in tests."""
    return patch(
        "app.api.v1.saml._require_authenticated_org_admin",
        return_value="user_test_admin",
    )


class TestSamlConfigCrud:
    """Tests for GET/PUT /saml/config/{org_id}."""

    def test_get_config_returns_not_configured_when_missing(self, client, mock_db):
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        with _mock_admin_auth():
            response = client.get("/api/v1/auth/saml/config/org_test123")
        assert response.status_code == 200
        data = response.json()
        assert data["configured"] is False

    def test_put_config_creates_new_config(self, client, mock_db):
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        with _mock_admin_auth():
            response = client.put(
                "/api/v1/auth/saml/config/org_test123",
                json={
                    "idp_entity_id": "https://idp.example.com/entity",
                    "idp_sso_url": "https://idp.example.com/sso",
                    "idp_certificate": "-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
                    "enabled": False,
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_put_config_updates_existing_config(self, client, mock_db):
        existing = MagicMock()
        existing.idp_entity_id = "old-entity"
        existing.idp_sso_url = "old-url"
        existing.idp_certificate = "old-cert"
        existing.attribute_mapping = {}
        existing.enabled = False

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = existing
        mock_db.query.return_value = mock_query

        with _mock_admin_auth():
            response = client.put(
                "/api/v1/auth/saml/config/org_test123",
                json={
                    "idp_entity_id": "https://new-idp.example.com/entity",
                    "enabled": True,
                },
            )
        assert response.status_code == 200
        assert existing.idp_entity_id == "https://new-idp.example.com/entity"
        assert existing.enabled is True

    def test_get_config_returns_configured_when_present(self, client, mock_db):
        existing = MagicMock()
        existing.organization_id = "org_test123"
        existing.idp_entity_id = "https://idp.example.com/entity"
        existing.idp_sso_url = "https://idp.example.com/sso"
        existing.idp_certificate = "cert-data"
        existing.attribute_mapping = {"email": "mail"}
        existing.enabled = True

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = existing
        mock_db.query.return_value = mock_query

        with _mock_admin_auth():
            response = client.get("/api/v1/auth/saml/config/org_test123")
        assert response.status_code == 200
        data = response.json()
        assert data["configured"] is True
        assert data["idp_entity_id"] == "https://idp.example.com/entity"
        assert data["has_certificate"] is True

    def test_get_config_rejects_unauthenticated(self, client, mock_db):
        """Config endpoints must reject unauthenticated requests."""
        response = client.get("/api/v1/auth/saml/config/org_test123")
        assert response.status_code == 401

    def test_put_config_rejects_unauthenticated(self, client, mock_db):
        """Config endpoints must reject unauthenticated requests."""
        response = client.put(
            "/api/v1/auth/saml/config/org_test123",
            json={"enabled": True},
        )
        assert response.status_code == 401


class TestSamlAcsUpdated:
    """Tests for the updated ACS endpoint that processes SAML assertions."""

    def test_acs_rejects_missing_relay_state(self, client):
        saml_xml = (
            '<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">'
            '<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">'
            "<saml:Subject><saml:NameID>user@example.com</saml:NameID></saml:Subject>"
            "</saml:Assertion>"
            "</samlp:Response>"
        )
        encoded = base64.b64encode(saml_xml.encode()).decode()
        response = client.post(
            "/api/v1/auth/saml/acs",
            data={"SAMLResponse": encoded},
        )
        assert response.status_code == 400

    def test_acs_rejects_invalid_relay_state(self, client):
        saml_xml = "<Response/>"
        encoded = base64.b64encode(saml_xml.encode()).decode()
        response = client.post(
            "/api/v1/auth/saml/acs",
            data={"SAMLResponse": encoded, "RelayState": "not-a-jwt"},
        )
        assert response.status_code == 400

    def test_acs_rejects_invalid_saml_encoding(self, client):
        response = client.post(
            "/api/v1/auth/saml/acs",
            data={"SAMLResponse": "!!!not-base64!!!"},
        )
        assert response.status_code in {400, 422}


class TestSamlMetadataEndpoint:
    """Metadata endpoint tests (unchanged behavior)."""

    def test_metadata_returns_xml_with_org_id(self, client):
        response = client.get("/api/v1/auth/saml/metadata", params={"org_id": "org_abc"})
        assert response.status_code == 200
        assert "xml" in response.headers.get("content-type", "")
        assert "urn:encypher:auth:org_abc" in response.text

    def test_metadata_requires_org_id(self, client):
        response = client.get("/api/v1/auth/saml/metadata")
        assert response.status_code == 422
