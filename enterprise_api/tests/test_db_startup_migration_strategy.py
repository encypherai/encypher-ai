"""Tests for startup DB migration strategy selection."""

from unittest.mock import MagicMock

import pytest

from app.utils import db_startup


def test_ensure_database_ready_defaults_to_alembic(monkeypatch):
    monkeypatch.setattr(db_startup, "check_database_connection", MagicMock())
    run_alembic = MagicMock(return_value=True)
    run_sql = MagicMock(return_value=True)
    monkeypatch.setattr(db_startup, "run_alembic_migrations", run_alembic)
    monkeypatch.setattr(db_startup, "run_sql_migrations", run_sql)

    ok = db_startup.ensure_database_ready(
        database_url="postgresql+asyncpg://user:pass@127.0.0.1:5432/db",
        service_name="enterprise-api-tests",
        run_migrations=True,
        exit_on_failure=False,
    )

    assert ok is True
    run_alembic.assert_called_once()
    run_sql.assert_not_called()


def test_ensure_database_ready_can_use_legacy_sql_strategy(monkeypatch):
    monkeypatch.setattr(db_startup, "check_database_connection", MagicMock())
    run_alembic = MagicMock(return_value=True)
    run_sql = MagicMock(return_value=True)
    monkeypatch.setattr(db_startup, "run_alembic_migrations", run_alembic)
    monkeypatch.setattr(db_startup, "run_sql_migrations", run_sql)

    ok = db_startup.ensure_database_ready(
        database_url="postgresql+asyncpg://user:pass@127.0.0.1:5432/db",
        service_name="enterprise-api-tests",
        run_migrations=True,
        migration_strategy="sql_legacy",
        migrations_dir="/tmp/migrations",
        exit_on_failure=False,
    )

    assert ok is True
    run_sql.assert_called_once()
    run_alembic.assert_not_called()


def test_ensure_database_ready_rejects_unknown_strategy(monkeypatch):
    monkeypatch.setattr(db_startup, "check_database_connection", MagicMock())

    with pytest.raises(db_startup.DatabaseStartupError, match="Unsupported migration strategy"):
        db_startup.ensure_database_ready(
            database_url="postgresql+asyncpg://user:pass@127.0.0.1:5432/db",
            service_name="enterprise-api-tests",
            run_migrations=True,
            migration_strategy="something_else",
            exit_on_failure=False,
        )


def test_run_alembic_migrations_injects_database_url_into_subprocess_env(monkeypatch):
    captured: dict = {}

    class Completed:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(cmd, cwd, check, capture_output, text, env):
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        captured["env"] = env
        return Completed()

    monkeypatch.setattr(db_startup.subprocess, "run", fake_run)

    db_startup.run_alembic_migrations(
        service_name="enterprise-api-tests",
        database_url="postgresql+asyncpg://user:pass@127.0.0.1:5432/db",
    )

    assert captured["cmd"][-2:] == ["upgrade", "heads"]
    assert captured["env"]["DATABASE_URL"] == "postgresql+asyncpg://user:pass@127.0.0.1:5432/db"
