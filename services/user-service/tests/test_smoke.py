import importlib
import sys


def test_app_imports(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    sys.modules.pop("app.core.config", None)
    sys.modules.pop("app.main", None)

    module = importlib.import_module("app.main")
    assert hasattr(module, "app")
