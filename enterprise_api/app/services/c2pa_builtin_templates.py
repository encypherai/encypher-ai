from __future__ import annotations

from typing import Any, Dict


BUILTIN_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "tmpl_builtin_all_rights_reserved_v1": {
        "id": "tmpl_builtin_all_rights_reserved_v1",
        "name": "All Rights Reserved",
        "description": "Default copyright protection. No AI training, inference, or data mining.",
        "schema_id": "schema_builtin_training_mining_v1",
        "template_data": {
            "assertions": [
                {
                    "label": "c2pa.training-mining.v1",
                    "default_data": {
                        "use": {
                            "ai_training": False,
                            "ai_inference": False,
                            "data_mining": False,
                        },
                        "constraint_info": {
                            "license": "All Rights Reserved",
                        },
                    },
                }
            ]
        },
        "category": "publisher",
        "organization_id": "org_builtin",
        "is_default": False,
        "is_active": True,
        "is_public": True,
        "created_at": None,
        "updated_at": None,
    },
    "tmpl_builtin_no_ai_training_v1": {
        "id": "tmpl_builtin_no_ai_training_v1",
        "name": "No AI Training",
        "description": "Disallow AI training and data mining.",
        "schema_id": "schema_builtin_training_mining_v1",
        "template_data": {
            "assertions": [
                {
                    "label": "c2pa.training-mining.v1",
                    "default_data": {
                        "use": {
                            "ai_training": False,
                            "ai_inference": True,
                            "data_mining": False,
                        },
                        "constraint_info": {
                            "license": "No AI Training",
                        },
                    },
                }
            ]
        },
        "category": "publisher",
        "organization_id": "org_builtin",
        "is_default": False,
        "is_active": True,
        "is_public": True,
        "created_at": None,
        "updated_at": None,
    }
    ,
    "tmpl_builtin_rag_allowed_with_attribution_v1": {
        "id": "tmpl_builtin_rag_allowed_with_attribution_v1",
        "name": "RAG Allowed (Attribution Required)",
        "description": "Allow retrieval-augmented generation with attribution; disallow training.",
        "schema_id": "schema_builtin_training_mining_v1",
        "template_data": {
            "assertions": [
                {
                    "label": "c2pa.training-mining.v1",
                    "default_data": {
                        "use": {
                            "ai_training": False,
                            "ai_inference": True,
                            "data_mining": True,
                        },
                        "constraint_info": {
                            "license": "RAG Allowed (Attribution Required)",
                            "attribution_required": True,
                        },
                    },
                }
            ]
        },
        "category": "publisher",
        "organization_id": "org_builtin",
        "is_default": False,
        "is_active": True,
        "is_public": True,
        "created_at": None,
        "updated_at": None,
    },
    "tmpl_builtin_realtime_quotes_with_attribution_v1": {
        "id": "tmpl_builtin_realtime_quotes_with_attribution_v1",
        "name": "Real-time Quotes Allowed (Attribution Required)",
        "description": "Allow real-time quotes with attribution; disallow training.",
        "schema_id": "schema_builtin_training_mining_v1",
        "template_data": {
            "assertions": [
                {
                    "label": "c2pa.training-mining.v1",
                    "default_data": {
                        "use": {
                            "ai_training": False,
                            "ai_inference": True,
                            "data_mining": False,
                        },
                        "constraint_info": {
                            "license": "Real-time Quotes Allowed (Attribution Required)",
                            "attribution_required": True,
                        },
                    },
                }
            ]
        },
        "category": "publisher",
        "organization_id": "org_builtin",
        "is_default": False,
        "is_active": True,
        "is_public": True,
        "created_at": None,
        "updated_at": None,
    },
}


def get_builtin_template(*, template_id: str) -> Dict[str, Any] | None:
    return BUILTIN_TEMPLATES.get(template_id)
