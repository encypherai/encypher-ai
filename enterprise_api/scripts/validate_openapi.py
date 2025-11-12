"""Generate and validate the FastAPI OpenAPI document."""
import json
from pathlib import Path

from fastapi.encoders import jsonable_encoder

from app.main import app


def main() -> None:
    schema = jsonable_encoder(app.openapi())
    output_path = Path("enterprise_api/docs/openapi.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(schema, indent=2))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
