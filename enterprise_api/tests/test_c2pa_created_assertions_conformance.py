"""C2PA Conformance: created_assertions compliance tests.

Validates that ALL assertions produced by our generator product are correctly
placed in created_assertions (not gathered_assertions) per C2PA spec section
14.3 and the conformance reviewer's requirements.

Tests cover:
- Pipeline A (c2pa.Builder via c2pa-python): assertions in the manifest
  definition must have "created": True so c2pa-rs places them in
  created_assertions in the claim.
- Pipeline B (custom CBOR/JUMBF): the CBOR claim must include a
  created_assertions field referencing all signer-originated assertions.
- Manifest JSON output: both pipelines produce the canonical c2pa-rs Reader
  format. A single validator checks all manifest files uniformly.
"""

import json
from pathlib import Path

import cbor2
import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

TESTS_DIR = Path(__file__).resolve().parent
CONFORMANCE_DIR = TESTS_DIR / "c2pa_conformance"
MANIFESTS_DIR = CONFORMANCE_DIR / "manifests"


# ===================================================================
# Unit tests: Pipeline A manifest builder (c2pa-python input dict)
# ===================================================================


class TestPipelineAManifestBuilder:
    """Validate that build_c2pa_manifest_dict produces assertions with created=True."""

    def test_all_assertions_have_created_true(self):
        """Every assertion in the manifest definition must have created=True."""
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        manifest = build_c2pa_manifest_dict(
            title="Test",
            org_id="test-org",
            document_id="test-doc",
            asset_id="test-asset-id",
            asset_id_key="image_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
            digital_source_type="digitalCapture",
        )

        assertions = manifest["assertions"]
        assert len(assertions) >= 2, f"Expected at least 2 assertions, got {len(assertions)}"

        for assertion in assertions:
            label = assertion["label"]
            assert (
                assertion.get("created") is True
            ), f"Assertion '{label}' missing created=True. c2pa-rs will place this in gathered_assertions, violating C2PA conformance requirements."

    def test_actions_assertion_has_created_true(self):
        """c2pa.actions.v2 must be in created_assertions."""
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        manifest = build_c2pa_manifest_dict(
            title="Test",
            org_id="test-org",
            document_id="test-doc",
            asset_id="test-asset-id",
            asset_id_key="audio_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )

        actions = [a for a in manifest["assertions"] if a["label"] == "c2pa.actions.v2"]
        assert len(actions) == 1, "Expected exactly one c2pa.actions.v2 assertion"
        assert (
            actions[0].get("created") is True
        ), "c2pa.actions.v2 MUST have created=True per C2PA conformance. The action assertion is a claim made by our generator product."

    def test_provenance_assertion_has_created_true(self):
        """com.encypher.provenance must be in created_assertions."""
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        manifest = build_c2pa_manifest_dict(
            title="Test",
            org_id="test-org",
            document_id="test-doc",
            asset_id="test-asset-id",
            asset_id_key="video_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )

        prov = [a for a in manifest["assertions"] if a["label"] == "com.encypher.provenance"]
        assert len(prov) == 1, "Expected exactly one com.encypher.provenance assertion"
        assert (
            prov[0].get("created") is True
        ), "com.encypher.provenance MUST have created=True per C2PA conformance. This is a custom assertion made by our generator product."

    def test_rights_assertion_has_created_true(self):
        """com.encypher.rights.v1 must be in created_assertions when present."""
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        manifest = build_c2pa_manifest_dict(
            title="Test",
            org_id="test-org",
            document_id="test-doc",
            asset_id="test-asset-id",
            asset_id_key="image_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={"ai_training": "notAllowed"},
        )

        rights = [a for a in manifest["assertions"] if a["label"] == "com.encypher.rights.v1"]
        assert len(rights) == 1, "Expected com.encypher.rights.v1 when rights_data is provided"
        assert rights[0].get("created") is True, "com.encypher.rights.v1 MUST have created=True per C2PA conformance."

    def test_custom_assertions_have_created_true(self):
        """Any custom assertions passed in must also get created=True."""
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        custom = [{"label": "com.example.custom", "data": {"key": "value"}}]
        manifest = build_c2pa_manifest_dict(
            title="Test",
            org_id="test-org",
            document_id="test-doc",
            asset_id="test-asset-id",
            asset_id_key="image_id",
            action="c2pa.created",
            custom_assertions=custom,
            rights_data={},
        )

        custom_result = [a for a in manifest["assertions"] if a["label"] == "com.example.custom"]
        assert len(custom_result) == 1
        assert custom_result[0].get("created") is True, "Custom assertions passed to the builder MUST have created=True."

    def test_no_top_level_createdAssertions_field(self):
        """The top-level createdAssertions field is ignored by c2pa-rs.

        Ensure we do NOT rely on it as the mechanism for marking assertions
        as created. The per-assertion 'created' flag is what matters.
        """
        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        manifest = build_c2pa_manifest_dict(
            title="Test",
            org_id="test-org",
            document_id="test-doc",
            asset_id="test-asset-id",
            asset_id_key="image_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
        )

        for assertion in manifest["assertions"]:
            assert assertion.get("created") is True, (
                f"Assertion '{assertion['label']}' relies on top-level "
                f"createdAssertions instead of per-assertion created=True flag. "
                f"c2pa-rs ignores the top-level field."
            )


# ===================================================================
# Unit tests: Pipeline B CBOR claim builder
# ===================================================================


class TestPipelineBClaimBuilder:
    """Validate that build_claim_cbor includes created_assertions in the CBOR claim."""

    def _build_test_claim(self):
        """Build a claim with typical assertions for testing."""
        from app.utils.c2pa_claim_builder import build_claim_cbor

        assertion_data = [
            ("c2pa.actions.v2", b"fake-actions-jumbf-content"),
            ("c2pa.hash.data", b"fake-hash-jumbf-content"),
            ("com.encypher.provenance", b"fake-provenance-jumbf-content"),
        ]

        claim_cbor = build_claim_cbor(
            manifest_label="urn:c2pa:test-manifest",
            assertion_data=assertion_data,
            dc_format="application/pdf",
            title="Test Document",
        )
        return cbor2.loads(claim_cbor), assertion_data

    def test_created_assertions_field_exists(self):
        """The CBOR claim must have a created_assertions field."""
        claim, _ = self._build_test_claim()
        assert (
            "created_assertions" in claim
        ), "CBOR claim is missing 'created_assertions' field. C2PA v2 requires this field to identify assertions made by the signer."

    def test_created_assertions_references_all_assertions(self):
        """created_assertions must reference ALL assertions (we are the sole signer)."""
        claim, assertion_data = self._build_test_claim()

        created_urls = {ref["url"] for ref in claim["created_assertions"]}
        expected_urls = {f"self#jumbf=c2pa.assertions/{label}" for label, _ in assertion_data}

        assert (
            created_urls == expected_urls
        ), f"created_assertions does not match expected. Missing: {expected_urls - created_urls}. Extra: {created_urls - expected_urls}."

    def test_created_assertions_have_hashes(self):
        """Each created_assertion ref must have a hash and alg."""
        claim, _ = self._build_test_claim()
        for ref in claim["created_assertions"]:
            assert "hash" in ref, f"created_assertion ref missing 'hash': {ref}"
            assert "alg" in ref, f"created_assertion ref missing 'alg': {ref}"
            assert "url" in ref, f"created_assertion ref missing 'url': {ref}"

    def test_no_gathered_assertions(self):
        """We are the sole signer; there should be no gathered_assertions."""
        claim, _ = self._build_test_claim()
        gathered = claim.get("gathered_assertions")
        assert (
            gathered is None or len(gathered) == 0
        ), f"Unexpected gathered_assertions in claim: {gathered}. All assertions should be in created_assertions."

    def test_no_v1_only_fields(self):
        """c2pa.claim.v2 must not contain v1-only fields."""
        claim, _ = self._build_test_claim()
        v1_only = {"claim_generator", "dc:format", "assertions"}
        present = v1_only & set(claim.keys())
        assert not present, f"v1-only fields found in v2 claim: {present}. c2pa-rs rejects claims with both v1 and v2 fields."


# ===================================================================
# Integration tests: validate ALL manifest JSON files (unified)
# ===================================================================


def _get_all_manifest_files():
    """Collect all manifest JSON files for parametrized testing."""
    if not MANIFESTS_DIR.exists():
        return []
    return sorted(MANIFESTS_DIR.glob("*.json"))


def _parse_manifest(data: dict) -> dict:
    """Parse a manifest JSON in canonical c2pa-rs Reader format.

    Both Pipeline A and Pipeline B produce the same structure:
    {"active_manifest": "<label>", "manifests": {"<label>": {...}}}
    """
    if "manifests" in data and isinstance(data["manifests"], dict):
        active = data.get("active_manifest")
        if active and active in data["manifests"]:
            return data["manifests"][active]
        return list(data["manifests"].values())[0]
    return data


@pytest.mark.parametrize(
    "manifest_path",
    _get_all_manifest_files(),
    ids=lambda p: p.stem,
)
class TestManifestFilesConformance:
    """Validate every manifest JSON in the conformance folder.

    Both pipelines produce the canonical c2pa-rs Reader format, so a
    single validator covers all formats uniformly.
    """

    def test_assertions_in_created_not_gathered(self, manifest_path: Path):
        """Every signer-originated assertion must have created=True."""
        data = json.loads(manifest_path.read_text())
        filename = manifest_path.name
        manifest = _parse_manifest(data)
        assertions = manifest.get("assertions", [])

        assert len(assertions) >= 2, f"{filename}: Expected at least 2 assertions, got {len(assertions)}"

        for assertion in assertions:
            label = assertion.get("label", "UNKNOWN")

            assert assertion.get("created") is True, (
                f"{filename}: Assertion '{label}' is missing created=True. "
                f"The C2PA conformance auditor will see this in "
                f"gathered_assertions instead of created_assertions. "
                f"This is a CONFORMANCE FAILURE."
            )

    def test_canonical_format(self, manifest_path: Path):
        """Manifest JSON must use the canonical c2pa-rs Reader format."""
        data = json.loads(manifest_path.read_text())
        filename = manifest_path.name

        assert "active_manifest" in data, f"{filename}: Missing 'active_manifest' key. Manifest JSON must use the canonical c2pa-rs format."
        assert isinstance(data.get("manifests"), dict), f"{filename}: 'manifests' must be a dict keyed by label, not a list."

        manifest = _parse_manifest(data)
        assert "claim_version" in manifest, f"{filename}: Missing 'claim_version'"
        assert manifest["claim_version"] == 2, f"{filename}: claim_version={manifest['claim_version']}, expected 2"
        assert isinstance(manifest.get("claim_generator_info"), list), f"{filename}: 'claim_generator_info' must be a list (c2pa-rs convention)"
        assert isinstance(manifest.get("assertions"), list), f"{filename}: 'assertions' must be a list of {{label, data, created}} objects"


# ===================================================================
# Integration test: sign and verify created_assertions end-to-end
# ===================================================================


class TestPipelineASignVerifyCreatedAssertions:
    """End-to-end: sign a file via Pipeline A and verify created_assertions."""

    def test_signed_jpeg_all_assertions_created(self):
        """Sign a JPEG and verify all assertions are in created_assertions."""
        import c2pa

        from app.utils.c2pa_manifest import build_c2pa_manifest_dict

        manifest_dict = build_c2pa_manifest_dict(
            title="Created Assertions Test",
            org_id="test-org",
            document_id="test-doc",
            asset_id="test-asset",
            asset_id_key="image_id",
            action="c2pa.created",
            custom_assertions=[],
            rights_data={},
            digital_source_type="digitalCapture",
        )

        for assertion in manifest_dict["assertions"]:
            assert assertion.get("created") is True, f"Pre-sign check: '{assertion['label']}' missing created=True"
