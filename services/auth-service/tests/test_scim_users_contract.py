from hashlib import sha256
from unittest.mock import MagicMock

import pytest


SCIM_LIST_RESPONSE_SCHEMA = "urn:ietf:params:scim:api:messages:2.0:ListResponse"
SCIM_USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"


def _hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def _make_scim_token(org_id: str = "org_test") -> str:
    return f"scim.{org_id}.testtoken"


@pytest.fixture
def scim_auth(mock_db):
    token = _make_scim_token()

    org = MagicMock()
    org.id = "org_test"
    org.features = {"scim_bearer_token_hash": _hash_token(token)}

    org_query = MagicMock()
    org_query.filter.return_value.first.return_value = org

    user_in_org = MagicMock()
    user_in_org.id = "user_in_org"
    user_in_org.email = "in-org@example.com"
    user_in_org.name = "In Org"
    user_in_org.is_active = True

    user_other = MagicMock()
    user_other.id = "user_other"
    user_other.email = "other-org@example.com"
    user_other.name = "Other Org"
    user_other.is_active = True

    user_query = MagicMock()
    user_query.all.return_value = [user_in_org, user_other]
    user_query.filter.return_value.first.return_value = None

    joined_query = user_query.join.return_value
    org_filtered_query = joined_query.filter.return_value
    org_filtered_query.all.return_value = [user_in_org]
    id_filtered_query = org_filtered_query.filter.return_value
    id_filtered_query.first.return_value = None

    from app.db.models import Organization, User

    def query(model):
        if model is Organization:
            return org_query
        if model is User:
            return user_query
        return MagicMock()

    mock_db.query.side_effect = query

    return {
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "user_query": user_query,
        "user_in_org": user_in_org,
        "user_other": user_other,
    }


@pytest.fixture
def scim_auth_cross_tenant_user(mock_db):
    token = _make_scim_token()

    org = MagicMock()
    org.id = "org_test"
    org.features = {"scim_bearer_token_hash": _hash_token(token)}

    org_query = MagicMock()
    org_query.filter.return_value.first.return_value = org

    user_other = MagicMock()
    user_other.id = "user_other"
    user_other.email = "other-org@example.com"
    user_other.name = "Other Org"
    user_other.is_active = True

    user_query = MagicMock()
    user_query.filter.return_value.first.return_value = user_other

    joined_query = user_query.join.return_value
    org_filtered_query = joined_query.filter.return_value
    id_filtered_query = org_filtered_query.filter.return_value
    id_filtered_query.first.return_value = None

    from app.db.models import Organization, User

    def query(model):
        if model is Organization:
            return org_query
        if model is User:
            return user_query
        return MagicMock()

    mock_db.query.side_effect = query

    return {
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def scim_auth_idempotent_membership(mock_db):
    token = _make_scim_token()

    org = MagicMock()
    org.id = "org_test"
    org.features = {"scim_bearer_token_hash": _hash_token(token)}

    org_query = MagicMock()
    org_query.filter.return_value.first.return_value = org

    existing_user = MagicMock()
    existing_user.id = "user_existing"
    existing_user.email = "alice@example.com"
    existing_user.name = "Alice Existing"
    existing_user.is_active = True

    user_query = MagicMock()
    user_query.filter.return_value.first.side_effect = [None, existing_user]

    existing_member = MagicMock()

    member_query = MagicMock()
    member_query.filter.return_value.filter.return_value.first.side_effect = [None, existing_member]

    from app.db.models import Organization, OrganizationMember, User

    def query(model):
        if model is Organization:
            return org_query
        if model is User:
            return user_query
        if model is OrganizationMember:
            return member_query
        return MagicMock()

    mock_db.query.side_effect = query

    return {
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


class TestScimUsersContract:
    def test_list_users_requires_bearer_token(self, client):
        response = client.get("/scim/v2/Users")
        assert response.status_code == 401

    def test_list_users_returns_scim_list_response(self, client, scim_auth):
        response = client.get("/scim/v2/Users", headers=scim_auth["headers"])
        assert response.status_code == 200
        assert "scim" in response.headers.get("content-type", "")

        body = response.json()
        assert body["schemas"] == [SCIM_LIST_RESPONSE_SCHEMA]
        resources = body["Resources"]
        assert isinstance(resources, list)
        assert len(resources) == 1
        assert resources[0]["id"] == scim_auth["user_in_org"].id
        assert resources[0]["userName"] == scim_auth["user_in_org"].email
        assert resources[0]["id"] != scim_auth["user_other"].id
        assert body["totalResults"] == 1

    def test_create_user_requires_bearer_token(self, client):
        response = client.post(
            "/scim/v2/Users",
            json={"schemas": [SCIM_USER_SCHEMA], "userName": "alice@example.com"},
        )
        assert response.status_code == 401

    def test_create_user_returns_scim_user_resource(self, client, scim_auth):
        payload = {
            "schemas": [SCIM_USER_SCHEMA],
            "userName": "alice@example.com",
            "displayName": "Alice Example",
            "active": True,
        }
        response = client.post("/scim/v2/Users", json=payload, headers=scim_auth["headers"])
        assert response.status_code == 201
        assert "scim" in response.headers.get("content-type", "")

        body = response.json()
        assert body["schemas"] == [SCIM_USER_SCHEMA]
        assert body["userName"] == "alice@example.com"
        assert body["active"] is True
        assert isinstance(body["id"], str)
        assert body["id"]

    def test_create_user_does_not_duplicate_membership(self, client, mock_db, scim_auth_idempotent_membership):
        payload = {
            "schemas": [SCIM_USER_SCHEMA],
            "userName": "alice@example.com",
            "displayName": "Alice Example",
            "active": True,
        }

        response_1 = client.post("/scim/v2/Users", json=payload, headers=scim_auth_idempotent_membership["headers"])
        assert response_1.status_code == 201

        response_2 = client.post("/scim/v2/Users", json=payload, headers=scim_auth_idempotent_membership["headers"])
        assert response_2.status_code == 201

        from app.db.models import OrganizationMember

        member_add_calls = [
            call
            for call in mock_db.add.call_args_list
            if call.args and isinstance(call.args[0], OrganizationMember)
        ]
        assert len(member_add_calls) == 1

    def test_get_user_returns_404_when_not_found(self, client, scim_auth):
        response = client.get("/scim/v2/Users/user_does_not_exist", headers=scim_auth["headers"])
        assert response.status_code == 404

    def test_get_user_is_tenant_isolated(self, client, scim_auth_cross_tenant_user):
        response = client.get("/scim/v2/Users/user_other", headers=scim_auth_cross_tenant_user["headers"])
        assert response.status_code == 404
