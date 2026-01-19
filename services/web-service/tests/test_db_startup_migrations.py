from unittest.mock import MagicMock, patch

import pytest
from encypher_commercial_shared.db import startup


def test_ensure_database_ready_passes_database_url_to_migrations(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://env-user:env-pass@env-host:5432/env_db")

    with (
        patch.object(startup, "check_database_connection") as mock_check,
        patch.object(startup, "run_migrations_if_needed") as mock_run_migrations,
    ):
        mock_check.return_value = True
        mock_run_migrations.return_value = True

        startup.ensure_database_ready(
            database_url="postgresql://passed-user:passed-pass@passed-host:5432/passed_db",
            service_name="test-service",
            alembic_config_path="alembic.ini",
            run_migrations=True,
            exit_on_failure=False,
        )

        assert mock_run_migrations.call_args.kwargs.get("database_url") == "postgresql://passed-user:passed-pass@passed-host:5432/passed_db"


def test_run_migrations_if_needed_prefers_explicit_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://env-user:env-pass@env-host:5432/env_db")

    explicit_url = "postgresql://explicit-user:explicit-pass@explicit-host:5432/explicit_db"

    mock_alembic_cfg = MagicMock()
    mock_script = MagicMock()
    mock_script.get_current_head.return_value = "head"

    mock_context = MagicMock()
    mock_context.get_current_revision.return_value = "head"

    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = object()

    with (
        patch.object(startup.os.path, "exists", return_value=True),
        patch("alembic.config.Config", return_value=mock_alembic_cfg),
        patch("alembic.script.ScriptDirectory.from_config", return_value=mock_script),
        patch(
            "alembic.runtime.migration.MigrationContext.configure",
            return_value=mock_context,
        ),
        patch("sqlalchemy.create_engine", return_value=mock_engine) as mock_create_engine,
    ):
        result = startup.run_migrations_if_needed(
            alembic_config_path="alembic.ini",
            service_name="test-service",
            auto_upgrade=True,
            database_url=explicit_url,
        )

    assert result is True
    mock_create_engine.assert_called_once_with(explicit_url)
    mock_alembic_cfg.set_main_option.assert_called_with("sqlalchemy.url", explicit_url)
