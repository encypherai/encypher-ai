"""
Unit tests for C2PA validator service.
"""

import pytest

from app.services.c2pa_validator import STANDARD_C2PA_ACTIONS, C2PAValidator


class TestC2PAValidator:
    """Test C2PA validation service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = C2PAValidator()

    # Action Validation Tests

    def test_validate_standard_c2pa_action(self):
        """Test validation of standard C2PA actions."""
        for action in STANDARD_C2PA_ACTIONS:
            is_valid, error = self.validator.validate_action(action)
            assert is_valid is True
            assert error is None

    def test_standard_c2pa_assertions_include_v2_3_labels(self):
        """Validator should recognize v2.3 assertion labels."""
        assert "c2pa.actions.v2" in self.validator.standard_assertions
        assert "c2pa.ingredient.v3" in self.validator.standard_assertions
        assert "c2pa.metadata" in self.validator.standard_assertions

    def test_validate_custom_namespaced_action(self):
        """Test validation of custom namespaced actions."""
        is_valid, error = self.validator.validate_action("com.acme.custom_action")
        assert is_valid is True
        assert error is None

    def test_validate_invalid_action_format(self):
        """Test validation fails for invalid action format."""
        is_valid, error = self.validator.validate_action("invalid_action")
        assert is_valid is False
        assert "Invalid action format" in error

    # Ingredient Assertion Tests

    def test_validate_ingredient_assertion_valid(self):
        """Test validation of valid ingredient assertion."""
        label = "c2pa.ingredient.v3"
        data = {
            "ingredients": [
                {"title": "Previous version", "instance_id": "abc-123", "relationship": "inputTo"},
                {"title": "Source", "instance_id": "def-456", "relationship": "componentOf"},
            ]
        }

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_ingredient_assertion_invalid_relationship(self):
        """Test validation fails for invalid ingredient relationship."""
        label = "c2pa.ingredient.v3"
        data = {"ingredients": [{"title": "Bad", "instance_id": "abc-123", "relationship": "parentOf"}]}

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is False
        assert any("relationship" in str(error).lower() for error in errors)

    # Metadata Assertion Tests

    def test_validate_metadata_assertion_requires_context(self):
        """Test validation fails when metadata lacks JSON-LD context."""
        label = "c2pa.metadata"
        data = {"identifier": "doc_001", "document_id": "doc_001"}

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is False
        assert any("@context" in str(error) for error in errors)

    def test_validate_metadata_assertion_valid(self):
        """Test validation of valid JSON-LD metadata assertion."""
        label = "c2pa.metadata"
        data = {"@context": "https://schema.org", "@type": "CreativeWork", "identifier": "doc_001"}

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is True
        assert len(errors) == 0

    # Location Assertion Tests

    def test_validate_location_assertion_valid(self):
        """Test validation of valid location assertion."""
        label = "c2pa.location.v1"
        data = {"latitude": 37.7749, "longitude": -122.4194, "altitude": 16.0, "location_name": "San Francisco City Hall"}

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_location_assertion_missing_required(self):
        """Test validation fails when required fields are missing."""
        label = "c2pa.location.v1"
        data = {
            "latitude": 37.7749
            # Missing required longitude
        }

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is False
        assert len(errors) > 0
        assert any("longitude" in str(e).lower() for e in errors)

    def test_validate_location_assertion_invalid_latitude(self):
        """Test validation fails for out-of-range latitude."""
        label = "c2pa.location.v1"
        data = {
            "latitude": 95.0,  # Invalid: > 90
            "longitude": -122.4194,
        }

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_location_assertion_invalid_longitude(self):
        """Test validation fails for out-of-range longitude."""
        label = "c2pa.location.v1"
        data = {
            "latitude": 37.7749,
            "longitude": -200.0,  # Invalid: < -180
        }

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is False
        assert len(errors) > 0

    # AI Training/Mining Assertion Tests

    def test_validate_training_mining_assertion_valid(self):
        """Test validation of valid AI training/mining assertion."""
        label = "c2pa.training-mining.v1"
        data = {
            "use": {"ai_training": False, "ai_inference": True, "data_mining": False},
            "constraint_info": {"license": "CC-BY-NC-4.0", "license_url": "https://creativecommons.org/licenses/by-nc/4.0/"},
        }

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_training_mining_assertion_missing_use(self):
        """Test validation fails when 'use' object is missing."""
        label = "c2pa.training-mining.v1"
        data = {"constraint_info": {"license": "CC-BY-NC-4.0"}}

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_training_mining_assertion_incomplete_use(self):
        """Test validation fails when 'use' object is incomplete."""
        label = "c2pa.training-mining.v1"
        data = {
            "use": {
                "ai_training": False
                # Missing ai_inference and data_mining
            }
        }

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is False
        assert len(errors) > 0

    # Claim Review Assertion Tests

    def test_validate_claim_review_assertion_valid(self):
        """Test validation of valid claim review assertion."""
        label = "c2pa.claim_review.v1"
        data = {
            "claim_reviewed": "Statement being fact-checked",
            "rating": "True",
            "appearance_url": "https://example.com/article",
            "author": {"name": "FactCheck.org", "url": "https://factcheck.org"},
            "date_published": "2025-11-03T14:00:00Z",
            "url": "https://factcheck.org/review/12345",
        }

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_claim_review_assertion_missing_required(self):
        """Test validation fails when required fields are missing."""
        label = "c2pa.claim_review.v1"
        data = {
            "claim_reviewed": "Statement being fact-checked"
            # Missing required rating
        }

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is False
        assert len(errors) > 0

    # Thumbnail Assertion Tests

    def test_validate_thumbnail_assertion_valid(self):
        """Test validation of valid thumbnail assertion."""
        label = "c2pa.thumbnail.v1"
        data = {"format": "image/jpeg", "identifier": "thumb_123", "thumbnail": "base64_encoded_data_here"}

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_thumbnail_assertion_invalid_format(self):
        """Test validation fails for invalid image format."""
        label = "c2pa.thumbnail.v1"
        data = {
            "format": "image/bmp",  # Not in enum
            "thumbnail": "base64_data",
        }

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        assert is_valid is False
        assert len(errors) > 0

    # Custom Schema Registration Tests

    def test_register_custom_schema_valid(self):
        """Test registering a valid custom schema."""
        label = "com.test.custom.v1"
        schema = {"type": "object", "properties": {"field1": {"type": "string"}, "field2": {"type": "number"}}, "required": ["field1"]}

        # Should not raise exception
        self.validator.register_schema(label, schema)

        # Should be in cache
        assert label in self.validator.schema_cache

    def test_register_custom_schema_invalid(self):
        """Test registering an invalid schema raises error."""
        label = "com.test.invalid.v1"
        schema = {
            "type": "invalid_type"  # Invalid JSON Schema
        }

        with pytest.raises(ValueError, match="Invalid JSON Schema"):
            self.validator.register_schema(label, schema)

    def test_validate_against_custom_schema(self):
        """Test validation against a registered custom schema."""
        label = "com.test.legal.v1"
        schema = {
            "type": "object",
            "properties": {"case_number": {"type": "string"}, "jurisdiction": {"type": "string"}},
            "required": ["case_number"],
        }

        self.validator.register_schema(label, schema)

        # Valid data
        data = {"case_number": "2024-CV-12345", "jurisdiction": "California"}
        is_valid, errors, warnings = self.validator.validate_assertion(label, data, schema)
        assert is_valid is True
        assert len(errors) == 0

        # Invalid data (missing required field)
        data_invalid = {"jurisdiction": "California"}
        is_valid, errors, warnings = self.validator.validate_assertion(label, data_invalid, schema)
        assert is_valid is False
        assert len(errors) > 0

    # Batch Validation Tests

    def test_validate_custom_assertions_all_valid(self):
        """Test batch validation when all assertions are valid."""
        assertions = [
            {"label": "c2pa.location.v1", "data": {"latitude": 37.7749, "longitude": -122.4194}},
            {"label": "c2pa.training-mining.v1", "data": {"use": {"ai_training": False, "ai_inference": False, "data_mining": False}}},
        ]

        all_valid, results = self.validator.validate_custom_assertions(assertions, {})
        assert all_valid is True
        assert len(results["assertions"]) == 2
        assert all(a["valid"] for a in results["assertions"])

    def test_validate_custom_assertions_some_invalid(self):
        """Test batch validation when some assertions are invalid."""
        assertions = [
            {"label": "c2pa.location.v1", "data": {"latitude": 37.7749, "longitude": -122.4194}},
            {
                "label": "c2pa.location.v1",
                "data": {"latitude": 95.0, "longitude": -122.4194},  # Invalid latitude
            },
        ]

        all_valid, results = self.validator.validate_custom_assertions(assertions, {})
        assert all_valid is False
        assert len(results["assertions"]) == 2
        assert results["assertions"][0]["valid"] is True
        assert results["assertions"][1]["valid"] is False

    def test_validate_custom_assertions_missing_label(self):
        """Test batch validation handles missing labels."""
        assertions = [
            {
                "data": {"latitude": 37.7749, "longitude": -122.4194}
                # Missing label
            }
        ]

        all_valid, results = self.validator.validate_custom_assertions(assertions, {})
        assert all_valid is False
        assert len(results["assertions"]) == 1
        assert results["assertions"][0]["valid"] is False
        assert "Missing assertion label" in results["assertions"][0]["errors"]

    # Warning Tests

    def test_validate_unknown_assertion_generates_warning(self):
        """Test that unknown assertion labels generate warnings."""
        label = "com.unknown.assertion.v1"
        data = {"some_field": "some_value"}

        is_valid, errors, warnings = self.validator.validate_assertion(label, data)
        # Should be valid (no schema to validate against)
        assert is_valid is True
        # Should have warning about no schema
        assert len(warnings) > 0
        assert any("no registered schema" in w.lower() for w in warnings)
