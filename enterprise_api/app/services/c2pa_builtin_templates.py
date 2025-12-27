from __future__ import annotations

from typing import Any, Dict


BUILTIN_TEMPLATES: Dict[str, Dict[str, Any]] = {
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
    }
}


def get_builtin_template(*, template_id: str) -> Dict[str, Any] | None:
    return BUILTIN_TEMPLATES.get(template_id)
