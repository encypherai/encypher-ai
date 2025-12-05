"""Allow running c2pa_text as a module: python -m c2pa_text"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
