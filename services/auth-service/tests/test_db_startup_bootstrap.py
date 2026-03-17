import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import Column, MetaData, String, Table

AUTH_SERVICE_ROOT = Path(__file__).resolve().parents[1]
STARTUP_MODULE_PATH = AUTH_SERVICE_ROOT / "shared_libs" / "src" / "encypher_commercial_shared" / "db" / "startup.py"
MAIN_FILE_PATH = AUTH_SERVICE_ROOT / "app" / "main.py"

_spec = importlib.util.spec_from_file_location("auth_shared_db_startup", STARTUP_MODULE_PATH)
startup = importlib.util.module_from_spec(_spec)
assert _spec is not None and _spec.loader is not None
_spec.loader.exec_module(startup)


def test_ensure_database_ready_validates_metadata_after_migrations() -> None:
    with (
        patch.object(startup, "check_database_connection") as mock_check,
        patch.object(startup, "run_migrations_if_needed") as mock_run_migrations,
        patch.object(startup, "validate_database_schema") as mock_validate_schema,
    ):
        mock_check.return_value = True
        mock_run_migrations.return_value = True
        mock_validate_schema.return_value = True

        result = startup.ensure_database_ready(
            database_url="postgresql://db.example.invalid:5432/testdb",
            service_name="auth-service",
            alembic_config_path="alembic.ini",
            run_migrations=True,
            model_metadata="metadata",
            exit_on_failure=False,
        )

    assert result is True
    mock_validate_schema.assert_called_once_with(
        database_url="postgresql://db.example.invalid:5432/testdb",
        model_metadata="metadata",
        service_name="auth-service",
    )


def test_validate_database_schema_raises_for_missing_columns() -> None:
    metadata = MetaData()
    Table(
        "organizations",
        metadata,
        Column("id", String),
        Column("name", String),
        Column("parent_org_id", String),
    )

    mock_engine = MagicMock()
    mock_inspector = MagicMock()
    mock_inspector.get_table_names.return_value = ["organizations"]
    mock_inspector.get_columns.return_value = [{"name": "id"}, {"name": "name"}]

    with (
        patch("sqlalchemy.create_engine", return_value=mock_engine),
        patch("sqlalchemy.inspect", return_value=mock_inspector),
    ):
        with pytest.raises(startup.DatabaseStartupError, match=r"organizations -> parent_org_id"):
            startup.validate_database_schema(
                database_url="postgresql://db.example.invalid:5432/testdb",
                model_metadata=metadata,
                service_name="auth-service",
            )

    mock_engine.dispose.assert_called_once()


def test_auth_main_passes_model_metadata_to_database_ready_check() -> None:
    source = MAIN_FILE_PATH.read_text()

    assert "ensure_database_ready(" in source
    assert "run_migrations=True" in source
    assert "model_metadata=Base.metadata" in source
