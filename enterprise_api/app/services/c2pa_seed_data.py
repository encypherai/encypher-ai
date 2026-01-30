"""
C2PA Seed Data

Standard schemas and templates for C2PA assertions.
"""

from typing import Any, Dict, List


def get_standard_schemas() -> List[Dict[str, Any]]:
    """Get standard C2PA assertion schemas."""
    return [
        {
            "namespace": "c2pa",
            "label": "c2pa.location.v1",
            "version": "1.0",
            "description": "Geographic location information with GPS coordinates",
            "is_public": True,
            "schema": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number", "minimum": -90, "maximum": 90, "description": "Latitude in decimal degrees"},
                    "longitude": {"type": "number", "minimum": -180, "maximum": 180, "description": "Longitude in decimal degrees"},
                    "altitude": {"type": "number", "description": "Altitude in meters"},
                    "location_name": {"type": "string", "description": "Human-readable location name"},
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
            },
        },
        {
            "namespace": "c2pa",
            "label": "c2pa.training-mining.v1",
            "version": "1.0",
            "description": "AI training and data mining permissions",
            "is_public": True,
            "schema": {
                "type": "object",
                "properties": {
                    "use": {
                        "type": "object",
                        "properties": {
                            "ai_training": {"type": "boolean", "description": "Allow use for AI training"},
                            "ai_inference": {"type": "boolean", "description": "Allow use for AI inference"},
                            "data_mining": {"type": "boolean", "description": "Allow data mining"},
                        },
                        "required": ["ai_training", "ai_inference", "data_mining"],
                    },
                    "constraint_info": {
                        "type": "object",
                        "properties": {
                            "license": {"type": "string", "description": "License identifier"},
                            "license_url": {"type": "string", "format": "uri", "description": "URL to license terms"},
                        },
                    },
                },
                "required": ["use"],
            },
        },
        {
            "namespace": "c2pa",
            "label": "c2pa.claim_review.v1",
            "version": "1.0",
            "description": "Fact-checking and claim review information",
            "is_public": True,
            "schema": {
                "type": "object",
                "properties": {
                    "claim_reviewed": {"type": "string", "description": "The claim being reviewed"},
                    "rating": {"type": "string", "description": "Review rating or verdict"},
                    "appearance_url": {"type": "string", "format": "uri", "description": "URL where claim appears"},
                    "author": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Reviewer name"},
                            "url": {"type": "string", "format": "uri", "description": "Reviewer URL"},
                        },
                        "required": ["name"],
                    },
                    "date_published": {"type": "string", "format": "date-time", "description": "Review publication date"},
                    "url": {"type": "string", "format": "uri", "description": "URL to full review"},
                },
                "required": ["claim_reviewed", "rating"],
            },
        },
        {
            "namespace": "c2pa",
            "label": "c2pa.thumbnail.v1",
            "version": "1.0",
            "description": "Thumbnail image for content preview",
            "is_public": True,
            "schema": {
                "type": "object",
                "properties": {
                    "format": {"type": "string", "enum": ["image/jpeg", "image/png", "image/webp"], "description": "Image MIME type"},
                    "identifier": {"type": "string", "description": "Unique identifier for thumbnail"},
                    "thumbnail": {"type": "string", "description": "Base64-encoded image data"},
                },
                "required": ["format", "thumbnail"],
            },
        },
    ]


def get_standard_templates() -> List[Dict[str, Any]]:
    """Get standard C2PA assertion templates."""
    return [
        {
            "name": "News Article",
            "description": "Standard template for news articles with fact-checking and AI permissions",
            "category": "news",
            "is_public": True,
            "assertions": [
                {"label": "c2pa.actions.v2", "description": "Track content lifecycle"},
                {
                    "label": "c2pa.training-mining.v1",
                    "description": "AI training permissions",
                    "default_data": {"use": {"ai_training": False, "ai_inference": False, "data_mining": False}},
                },
                {"label": "c2pa.claim_review.v1", "description": "Fact-checking information", "optional": True},
                {"label": "c2pa.location.v1", "description": "Story location", "optional": True},
            ],
        },
        {
            "name": "Legal Document",
            "description": "Template for legal documents with strict provenance tracking",
            "category": "legal",
            "is_public": True,
            "assertions": [
                {"label": "c2pa.actions.v2", "description": "Complete audit trail"},
                {
                    "label": "c2pa.training-mining.v1",
                    "description": "Prohibit AI use",
                    "default_data": {
                        "use": {"ai_training": False, "ai_inference": False, "data_mining": False},
                        "constraint_info": {"license": "All Rights Reserved"},
                    },
                },
            ],
        },
        {
            "name": "Academic Paper",
            "description": "Template for academic papers with citation tracking",
            "category": "academic",
            "is_public": True,
            "assertions": [
                {"label": "c2pa.actions.v2", "description": "Research workflow tracking"},
                {
                    "label": "c2pa.training-mining.v1",
                    "description": "AI permissions for research",
                    "default_data": {
                        "use": {"ai_training": True, "ai_inference": True, "data_mining": True},
                        "constraint_info": {"license": "CC-BY-4.0"},
                    },
                },
            ],
        },
        {
            "name": "Publisher Content",
            "description": "Template for publisher content with copyright protection",
            "category": "publisher",
            "is_public": True,
            "assertions": [
                {"label": "c2pa.actions.v2", "description": "Publication workflow"},
                {
                    "label": "c2pa.training-mining.v1",
                    "description": "Copyright protection",
                    "default_data": {"use": {"ai_training": False, "ai_inference": False, "data_mining": False}},
                },
                {"label": "c2pa.thumbnail.v1", "description": "Content preview", "optional": True},
            ],
        },
    ]
