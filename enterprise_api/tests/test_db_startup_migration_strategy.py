"""Tests for startup DB migration strategy selection."""

import inspect
from unittest.mock import MagicMock

import pytest

from app.utils import db_startup


def test_ensure_database_ready_defaults_to_alembic(monkeypatch):
    monkeypatch.setattr(db_startup, "check_database_connection", MagicMock())
    run_alembic = MagicMock(return_value=True)
    monkeypatch.setattr(db_startup, "run_alembic_migrations", run_alembic)

    ok = db_startup.ensure_database_ready(
        database_url="postgresql+asyncpg://user:pass@127.0.0.1:5432/db",
        service_name="enterprise-api-tests",
        run_migrations=True,
        exit_on_failure=False,
    )

    assert ok is True
    run_alembic.assert_called_once()


def test_ensure_database_ready_signature_has_no_strategy_switch():
    signature = inspect.signature(db_startup.ensure_database_ready)
    assert "migration_strategy" not in signature.parameters
    assert "migrations_dir" not in signature.parameters


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

    assert captured["cmd"][-2:] == ["upgrade", "head"]
    assert captured["env"]["DATABASE_URL"] == "postgresql+asyncpg://user:pass@127.0.0.1:5432/db"
