import base64
import pytest


class TestSamlContract:
    def test_metadata_requires_org_id(self, client):
        response = client.get("/api/v1/auth/saml/metadata")
        assert response.status_code == 422

    def test_metadata_returns_xml(self, client):
        response = client.get("/api/v1/auth/saml/metadata", params={"org_id": "org_test"})
        assert response.status_code == 200
        assert "xml" in response.headers.get("content-type", "")
        assert "EntityDescriptor" in response.text

    def test_login_requires_org_id(self, client):
        response = client.get(
            "/api/v1/auth/saml/login",
            params={"return_to": "http://localhost:3001"},
            follow_redirects=False,
        )
        assert response.status_code == 422

    def test_login_redirects_with_samlrequest_and_relaystate(self, client):
        response = client.get(
            "/api/v1/auth/saml/login",
            params={"org_id": "org_test", "return_to": "http://localhost:3001"},
            follow_redirects=False,
        )
        assert response.status_code in {302, 303, 307}
        location = response.headers.get("location")
        assert location
        assert "SAMLRequest=" in location
        assert "RelayState=" in location

    @pytest.mark.parametrize(
        "return_to",
        [
            "https://evil.example.com/phish",
            "//evil.example.com/phish",
        ],
    )
    def test_login_rejects_untrusted_return_to(self, client, return_to):
        response = client.get(
            "/api/v1/auth/saml/login",
            params={"org_id": "org_test", "return_to": return_to},
            follow_redirects=False,
        )
        assert response.status_code == 400

    def test_acs_requires_samlresponse(self, client):
        response = client.post("/api/v1/auth/saml/acs")
        assert response.status_code == 422

    @pytest.mark.parametrize("saml_response", ["not-base64", "", "!!!!"])
    def test_acs_rejects_invalid_samlresponse(self, client, saml_response):
        response = client.post("/api/v1/auth/saml/acs", data={"SAMLResponse": saml_response})
        assert response.status_code in {400, 422}

    def test_acs_fails_closed_until_signature_validation_is_implemented(self, client):
        saml_response = base64.b64encode(b"<saml>ok</saml>").decode("ascii")
        response = client.post("/api/v1/auth/saml/acs", data={"SAMLResponse": saml_response})
        assert response.status_code == 501
