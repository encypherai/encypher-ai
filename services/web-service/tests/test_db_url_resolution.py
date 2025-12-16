import pytest

from app.core.config import Settings


def test_database_url_wins_over_postgres_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SQLALCHEMY_DATABASE_URI", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@db-host:5432/prod_db")

    monkeypatch.setenv("POSTGRES_SERVER", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres")
    monkeypatch.setenv("POSTGRES_DB", "local_db")

    settings = Settings(_env_file=None)

    assert str(settings.SQLALCHEMY_DATABASE_URI) == "postgresql://user:pass@db-host:5432/prod_db"


def test_postgres_scheme_is_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SQLALCHEMY_DATABASE_URI", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@db-host:5432/prod_db")

    settings = Settings(_env_file=None)

    assert str(settings.SQLALCHEMY_DATABASE_URI) == "postgresql+psycopg2://user:pass@db-host:5432/prod_db"
