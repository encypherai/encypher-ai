"""
C2PA Assertion Validation Service

Validates C2PA assertions against registered schemas.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import jsonschema
from jsonschema import Draft7Validator

logger = logging.getLogger(__name__)


# Standard C2PA actions from C2PA 2.2 specification
STANDARD_C2PA_ACTIONS = {
    "c2pa.created",
    "c2pa.edited",
    "c2pa.opened",
    "c2pa.placed",
    "c2pa.published",
    "c2pa.redacted",
    "c2pa.transcoded",
    "c2pa.translated",
    "c2pa.cropped",
    "c2pa.filtered",
    "c2pa.resized",
    "c2pa.orientation",
    "c2pa.color_adjustments",
    "c2pa.drawing",
    "c2pa.repackaged",
    "c2pa.watermarked",
}


# Standard C2PA assertion labels
STANDARD_C2PA_ASSERTIONS = {
    "c2pa.actions.v2",
    "c2pa.hash.data.v1",
    "c2pa.soft_binding.v1",
    "c2pa.metadata",
    "c2pa.location.v1",
    "c2pa.thumbnail.v1",
    "c2pa.data_hash.v1",
    "c2pa.ingredient.v3",
    "c2pa.training-mining.v1",
    "c2pa.claim_review.v1",
    "c2pa.creative_work.v1",
    "c2pa.exif.v1",
    "c2pa.schema-org.CreativeWork.v1",
    "stds.iptc.photo.v1",
    "stds.exif.v1",
}


class C2PAValidator:
    """
    Validates C2PA assertions against schemas.
    """

    def __init__(self):
        self.schema_cache: Dict[str, Any] = {}
        self.standard_assertions = STANDARD_C2PA_ASSERTIONS
        self._load_standard_schemas()

    def _load_standard_schemas(self):
        """Load standard C2PA assertion schemas."""
        # Location assertion schema
        self.schema_cache["c2pa.location.v1"] = {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "minimum": -90, "maximum": 90},
                "longitude": {"type": "number", "minimum": -180, "maximum": 180},
                "altitude": {"type": "number"},
                "location_name": {"type": "string"},
                "location_shown": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "city": {"type": "string"},
                        "state": {"type": "string"},
                        "country": {"type": "string"},
                    },
                },
            },
            "required": ["latitude", "longitude"],
        }

        # AI Training/Mining assertion schema
        self.schema_cache["c2pa.training-mining.v1"] = {
            "type": "object",
            "properties": {
                "use": {
                    "type": "object",
                    "properties": {"ai_training": {"type": "boolean"}, "ai_inference": {"type": "boolean"}, "data_mining": {"type": "boolean"}},
                    "required": ["ai_training", "ai_inference", "data_mining"],
                },
                "constraint_info": {
                    "type": "object",
                    "properties": {"license": {"type": "string"}, "license_url": {"type": "string", "format": "uri"}},
                },
            },
            "required": ["use"],
        }

        # Claim Review assertion schema
        self.schema_cache["c2pa.claim_review.v1"] = {
            "type": "object",
            "properties": {
                "claim_reviewed": {"type": "string"},
                "rating": {"type": "string"},
                "appearance_url": {"type": "string", "format": "uri"},
                "author": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "url": {"type": "string", "format": "uri"}},
                    "required": ["name"],
                },
                "date_published": {"type": "string", "format": "date-time"},
                "url": {"type": "string", "format": "uri"},
            },
            "required": ["claim_reviewed", "rating"],
        }

        # Thumbnail assertion schema
        self.schema_cache["c2pa.thumbnail.v1"] = {
            "type": "object",
            "properties": {
                "format": {"type": "string", "enum": ["image/jpeg", "image/png", "image/webp"]},
                "identifier": {"type": "string"},
                "thumbnail": {"type": "string"},  # Base64 encoded
            },
            "required": ["format", "thumbnail"],
        }

        # Ingredient assertion schema
        self.schema_cache["c2pa.ingredient.v3"] = {
            "type": "object",
            "properties": {
                "ingredients": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "instance_id": {"type": "string"},
                            "relationship": {"type": "string", "enum": ["componentOf", "inputTo"]},
                            "c2pa_manifest": {"type": "object"},
                        },
                        "required": ["instance_id", "relationship"],
                    },
                    "minItems": 1,
                }
            },
            "required": ["ingredients"],
        }

        # Metadata assertion schema (JSON-LD)
        self.schema_cache["c2pa.metadata"] = {
            "type": "object",
            "properties": {
                "@context": {"type": "string"},
                "@type": {"type": "string"},
                "identifier": {"type": "string"},
            },
            "required": ["@context"],
        }

        self.schema_cache["com.encypher.rights.v1"] = {
            "type": "object",
            "properties": {
                "copyright_holder": {"type": "string"},
                "license_url": {"type": "string", "format": "uri"},
                "usage_terms": {"type": "string"},
                "syndication_allowed": {"type": "boolean"},
                "embargo_until": {"type": "string", "format": "date-time"},
                "contact_email": {"type": "string", "format": "email"},
            },
        }

    def validate_action(self, action: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a C2PA action.

        Args:
            action: Action label (e.g., 'c2pa.created')

        Returns:
            Tuple of (is_valid, error_message)
        """
        if action in STANDARD_C2PA_ACTIONS:
            return True, None

        # Allow custom actions with proper namespace
        if action.startswith("c2pa.") or "." in action:
            logger.warning(f"Non-standard C2PA action: {action}")
            return True, None

        return False, f"Invalid action format: {action}. Must be a standard C2PA action or use namespace format (e.g., 'com.example.action')"

    def validate_assertion(
        self, label: str, data: Dict[str, Any], custom_schema: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate an assertion against its schema.

        Args:
            label: Assertion label (e.g., 'c2pa.location.v1')
            data: Assertion data to validate
            custom_schema: Optional custom schema for validation

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # Get schema
        schema = custom_schema if custom_schema else self.schema_cache.get(label)

        if not schema:
            if label in STANDARD_C2PA_ASSERTIONS:
                warnings.append(f"Standard assertion {label} has no validation schema loaded")
                return True, [], warnings
            else:
                # Custom assertion without schema
                warnings.append(f"Custom assertion {label} has no registered schema")
                return True, [], warnings

        # Validate against schema
        try:
            validator = Draft7Validator(schema)
            validation_errors = list(validator.iter_errors(data))

            if validation_errors:
                for error in validation_errors:
                    error_path = ".".join(str(p) for p in error.path) if error.path else "root"
                    errors.append(f"{error_path}: {error.message}")
                return False, errors, warnings

            return True, [], warnings

        except Exception as e:
            logger.error(f"Validation error for {label}: {e}")
            errors.append(f"Validation failed: {str(e)}")
            return False, errors, warnings

    def register_schema(self, label: str, schema: Dict[str, Any]):
        """
        Register a custom schema for validation.

        Args:
            label: Assertion label
            schema: JSON Schema for validation
        """
        # Validate the schema itself
        try:
            Draft7Validator.check_schema(schema)
            self.schema_cache[label] = schema
            logger.info(f"Registered schema for {label}")
        except jsonschema.SchemaError as e:
            logger.error(f"Invalid schema for {label}: {e}")
            raise ValueError(f"Invalid JSON Schema: {e}")

    def validate_custom_assertions(
        self, assertions: List[Dict[str, Any]], registered_schemas: Dict[str, Dict[str, Any]]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate a list of custom assertions.

        Args:
            assertions: List of assertions to validate
            registered_schemas: Dictionary of label -> schema

        Returns:
            Tuple of (all_valid, validation_results)
        """
        assertions_results: List[Dict[str, Any]] = []
        results: Dict[str, Any] = {"valid": True, "assertions": assertions_results}

        for assertion in assertions:
            label = assertion.get("label")
            data = assertion.get("data", {})

            if not label:
                results["valid"] = False
                assertions_results.append({"label": None, "valid": False, "errors": ["Missing assertion label"], "warnings": []})
                continue

            # Get schema
            schema = registered_schemas.get(label)

            # Validate
            is_valid, errors, warnings = self.validate_assertion(label, data, schema)

            if not is_valid:
                results["valid"] = False

            assertions_results.append({"label": label, "valid": is_valid, "errors": errors, "warnings": warnings})

        return results["valid"], results


# Global validator instance
validator = C2PAValidator()
