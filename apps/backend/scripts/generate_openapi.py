#!/usr/bin/env python3
"""Generate OpenAPI JSON specification from FastAPI application.

This script extracts the OpenAPI schema from the FastAPI app without
running the server. The generated openapi.json can be used for:
- SDK generation (mobile app, frontend clients)
- API documentation
- Schema alignment testing (verify implemented responses match the snapshot)

Usage:
    poetry run python scripts/generate_openapi.py
    # or
    python scripts/generate_openapi.py

Output:
    Creates/updates ../../openapi/openapi.json (repo root)
"""

import json
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from fastapi.openapi.utils import get_openapi


def generate_openapi_spec(output_path: str = "../../openapi/openapi.json") -> None:
    """Generate OpenAPI specification and save to file.

    Args:
        output_path: Path to output file (relative to this script)
    """
    # Import the FastAPI app
    from app.main import app

    # Generate OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        openapi_version=app.openapi_version,
    )

    # Resolve output path
    script_dir = Path(__file__).parent
    output_file = script_dir / output_path
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write to file with pretty formatting
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print(f"✅ OpenAPI specification generated successfully!")
    print(f"📄 Output: {output_file.resolve()}")
    print(f"📊 Endpoints: {len([r for r in app.routes if hasattr(r, 'methods')])}")
    print(f"🔖 Version: {app.version}")
    print()
    print("Next steps:")
    print("  1. Review the generated openapi.json")
    print("  2. Regenerate mobile SDK:")
    print("     cd apps/mobile")
    print("     npm run sdk:clean")
    print("     npm run sdk:generate")


if __name__ == "__main__":
    try:
        generate_openapi_spec()
    except Exception as e:
        print(f"❌ Error generating OpenAPI spec: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
