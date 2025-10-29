import importlib.util
import sys
from pathlib import Path


def _set_enterprise_app() -> None:
    root = Path(__file__).resolve().parents[1]
    app_init = root / "app" / "__init__.py"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location(
        "app",
        app_init,
        submodule_search_locations=[str(root / "app")],
    )
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules["app"] = module
        spec.loader.exec_module(module)


_set_enterprise_app()
