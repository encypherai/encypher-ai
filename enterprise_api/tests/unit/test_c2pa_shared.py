"""Unit tests for shared C2PA modules.

Tests for:
- app.utils.hashing (compute_sha256)
- app.utils.c2pa_manifest (build_c2pa_manifest_dict)
- app.utils.c2pa_verifier_core (verify_c2pa)
"""

from unittest.mock import MagicMock, patch

import pytest

from app.utils.hashing import compute_sha256


# ===========================================================================
# hashing: compute_sha256
# ===========================================================================


class TestComputeSha256:
    def test_known_hash(self):
        result = compute_sha256(b"hello")
        assert result.startswith("sha256:")
        assert len(result) == 7 + 64  # prefix + hex

    def test_deterministic(self):
        a = compute_sha256(b"test")
        b = compute_sha256(b"test")
        assert a == b

    def test_different_inputs(self):
        a = compute_sha256(b"foo")
        b = compute_sha256(b"bar")
        assert a != b

    def test_empty_bytes(self):
        result = compute_sha256(b"")
        assert result.startswith("sha256:")
        # SHA-256 of empty string is well-known
        assert result == "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


# ===========================================================================
# c2pa_manifest: build_c2pa_manifest_dict
# ===========================================================================


class TestBuildC2paManifestDict:
    def test_basic_structure(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.wav",
            org_id="org_123",
            document_id="doc_abc",
            asset_id="aud_xyz",
            asset_id_key="audio_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )

        assert result["claim_generator"] == "Encypher Enterprise API/1.0"
        assert result["title"] == "test.wav"
        assert result["instance_id"].startswith("urn:uuid:")
        assert isinstance(result["assertions"], list)

    def test_asset_id_key_in_provenance(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.jpg",
            org_id="org_123",
            document_id="doc_abc",
            asset_id="img_xyz",
            asset_id_key="image_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )

        # Find provenance assertion
        provenance = None
        for a in result["assertions"]:
            if a["label"] == "com.encypher.provenance":
                provenance = a["data"]
                break

        assert provenance is not None
        assert provenance["image_id"] == "img_xyz"
        assert provenance["organization_id"] == "org_123"
        assert provenance["document_id"] == "doc_abc"
        assert "audio_id" not in provenance

    def test_audio_asset_id_key(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.wav",
            org_id="org_123",
            document_id="doc_abc",
            asset_id="aud_xyz",
            asset_id_key="audio_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )

        provenance = None
        for a in result["assertions"]:
            if a["label"] == "com.encypher.provenance":
                provenance = a["data"]
                break

        assert provenance is not None
        assert provenance["audio_id"] == "aud_xyz"
        assert "image_id" not in provenance

    def test_rights_data_included_when_present(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.wav",
            org_id="org_123",
            document_id="doc_abc",
            asset_id="aud_xyz",
            asset_id_key="audio_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={"license": "CC-BY-4.0"},
        )

        labels = [a["label"] for a in result["assertions"]]
        assert "com.encypher.rights.v1" in labels

        rights = next(a for a in result["assertions"] if a["label"] == "com.encypher.rights.v1")
        assert rights["data"]["license"] == "CC-BY-4.0"

    def test_rights_data_excluded_when_empty(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.wav",
            org_id="org_123",
            document_id="doc_abc",
            asset_id="aud_xyz",
            asset_id_key="audio_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )

        labels = [a["label"] for a in result["assertions"]]
        assert "com.encypher.rights.v1" not in labels

    def test_custom_assertions_included(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        custom = [{"label": "com.example.custom", "data": {"key": "value"}}]
        result = build_c2pa_manifest_dict(
            title="test.wav",
            org_id="org_123",
            document_id="doc_abc",
            asset_id="aud_xyz",
            asset_id_key="audio_id",
            action="c2pa.created",
            custom_assertions=custom,
            rights_data={},
        )

        labels = [a["label"] for a in result["assertions"]]
        assert "com.example.custom" in labels

    def test_video_asset_id_key(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.mp4",
            org_id="org_123",
            document_id="doc_abc",
            asset_id="vid_xyz",
            asset_id_key="video_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )
        provenance = [a for a in result["assertions"] if a["label"] == "com.encypher.provenance"][0]
        assert provenance["data"]["video_id"] == "vid_xyz"
        assert "image_id" not in provenance["data"]
        assert "audio_id" not in provenance["data"]

    def test_action_in_assertions(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.wav",
            org_id="org_123",
            document_id="doc_abc",
            asset_id="aud_xyz",
            asset_id_key="audio_id",
            action="c2pa.dubbed",
            custom_assertions=[],
            rights_data={},
        )

        actions_assertion = next(a for a in result["assertions"] if a["label"] == "c2pa.actions.v2")
        actions = actions_assertion["data"]["actions"]
        # Section 15.4.1: first action must be c2pa.created or c2pa.opened.
        # Non-created/opened actions get c2pa.opened prepended automatically.
        assert actions[0]["action"] == "c2pa.opened"
        assert actions[1]["action"] == "c2pa.dubbed"
        assert "when" in actions[1]

    def test_actions_uses_v2_label(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.jpg",
            org_id="org_1",
            document_id="doc_1",
            asset_id="img_1",
            asset_id_key="image_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )
        labels = [a["label"] for a in result["assertions"]]
        assert "c2pa.actions.v2" in labels
        assert "c2pa.actions" not in labels

    def test_digital_source_type_on_created(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.jpg",
            org_id="org_1",
            document_id="doc_1",
            asset_id="img_1",
            asset_id_key="image_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )
        action_entry = next(a for a in result["assertions"] if a["label"] == "c2pa.actions.v2")["data"]["actions"][0]
        assert "digitalSourceType" in action_entry
        assert action_entry["digitalSourceType"].startswith("http://cv.iptc.org/")

    def test_digital_source_type_explicit(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.jpg",
            org_id="org_1",
            document_id="doc_1",
            asset_id="img_1",
            asset_id_key="image_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
            digital_source_type="trainedAlgorithmicMedia",
        )
        action_entry = next(a for a in result["assertions"] if a["label"] == "c2pa.actions.v2")["data"]["actions"][0]
        assert "trainedAlgorithmicMedia" in action_entry["digitalSourceType"]

    def test_no_digital_source_type_on_non_created(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.jpg",
            org_id="org_1",
            document_id="doc_1",
            asset_id="img_1",
            asset_id_key="image_id",
            action="c2pa.dubbed",
            custom_assertions=[],
            rights_data={},
        )
        action_entry = next(a for a in result["assertions"] if a["label"] == "c2pa.actions.v2")["data"]["actions"][0]
        assert "digitalSourceType" not in action_entry

    def test_software_agent_in_action(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.jpg",
            org_id="org_1",
            document_id="doc_1",
            asset_id="img_1",
            asset_id_key="image_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )
        action_entry = next(a for a in result["assertions"] if a["label"] == "c2pa.actions.v2")["data"]["actions"][0]
        assert "softwareAgent" in action_entry
        assert action_entry["softwareAgent"]["name"] == "Encypher Enterprise API"

    def test_claim_generator_info(self):
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        result = build_c2pa_manifest_dict(
            title="test.jpg",
            org_id="org_1",
            document_id="doc_1",
            asset_id="img_1",
            asset_id_key="image_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )
        info = result["claim_generator_info"]
        assert len(info) == 1
        assert info[0]["name"] == "Encypher"


# ===========================================================================
# c2pa_verifier_core: verify_c2pa
# ===========================================================================


class TestVerifyC2pa:
    def test_no_manifest_error(self):
        """When c2pa.Reader raises a 'not found' error, return valid=False."""
        from app.utils.c2pa_verifier_core import verify_c2pa

        with patch("app.utils.c2pa_verifier_core.c2pa", create=True) as mock_c2pa:
            import sys

            # Create a mock c2pa module
            mock_module = MagicMock()
            mock_module.Reader.side_effect = Exception("JumbfNotFound: no manifest")
            sys.modules["c2pa"] = mock_module

            result = verify_c2pa(b"\x00" * 100, "audio/wav")

            del sys.modules["c2pa"]

        assert result.valid is False
        assert result.error is not None

    def test_canonicalize_fn_applied(self):
        """The canonicalize_fn should be called on the mime_type."""
        from app.utils.c2pa_verifier_core import verify_c2pa

        called_with = []

        def track_canonicalize(mime: str) -> str:
            called_with.append(mime)
            return "audio/wav"

        # Will fail because no actual c2pa manifest, but canonicalize_fn should be called
        result = verify_c2pa(b"\x00" * 100, "audio/wave", canonicalize_fn=track_canonicalize)
        assert called_with == ["audio/wave"]

    def test_valid_manifest_parse(self):
        """With a mock Reader that returns valid JSON, verify_c2pa returns valid=True."""
        import json
        import sys
        from unittest.mock import MagicMock

        from app.utils.c2pa_verifier_core import verify_c2pa

        manifest_data = {
            "active_manifest": "self#jumbf=c2pa/urn:uuid:test-123",
            "manifests": {
                "self#jumbf=c2pa/urn:uuid:test-123": {
                    "instance_id": "urn:uuid:test-123",
                    "claim_generator": "encypher-ai/1.0",
                    "assertions": [
                        {
                            "label": "c2pa.actions",
                            "data": {"actions": [{"action": "c2pa.created", "when": "2026-01-01T00:00:00Z"}]},
                        }
                    ],
                }
            },
        }

        mock_reader = MagicMock()
        mock_reader.json.return_value = json.dumps(manifest_data)

        mock_module = MagicMock()
        mock_module.Reader.return_value = mock_reader
        sys.modules["c2pa"] = mock_module

        try:
            result = verify_c2pa(b"\x00" * 100, "audio/wav")
        finally:
            del sys.modules["c2pa"]

        assert result.valid is True
        assert result.c2pa_instance_id == "urn:uuid:test-123"
        assert result.signer == "encypher-ai/1.0"
        assert result.signed_at == "2026-01-01T00:00:00Z"

    def test_generic_exception(self):
        """Non-manifest errors should be reported as verification failures."""
        import sys
        from unittest.mock import MagicMock

        from app.utils.c2pa_verifier_core import verify_c2pa

        mock_module = MagicMock()
        mock_module.Reader.side_effect = RuntimeError("unexpected internal error")
        sys.modules["c2pa"] = mock_module

        try:
            result = verify_c2pa(b"\x00" * 100, "audio/wav")
        finally:
            del sys.modules["c2pa"]

        assert result.valid is False
        assert result.error == "C2PA verification failed"
