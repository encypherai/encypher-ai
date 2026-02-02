from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient


@dataclass(frozen=True)
class LocalApiConfig:
    api_key: str
    base_url: str
    timeout_seconds: float = 30.0


def _load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    env_vars: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        candidate = line.strip()
        if not candidate or candidate.startswith("#"):
            continue
        if "=" not in candidate:
            continue
        key, value = candidate.split("=", 1)
        env_vars[key.strip()] = value.strip()
    return env_vars


@pytest.fixture(scope="session")
def local_api_config() -> LocalApiConfig:
    if os.getenv("LOCAL_API_TESTS", "").lower() != "true":
        pytest.skip("Local API tests disabled. Set LOCAL_API_TESTS=true to run.")

    env_path = Path(__file__).with_name(".env.local")
    env_vars = _load_env_file(env_path)

    api_key = os.getenv("LOCAL_API_KEY") or os.getenv("API_KEY") or env_vars.get("API_KEY")
    base_url = os.getenv("LOCAL_API_BASE_URL") or os.getenv("BASE_URL") or env_vars.get("BASE_URL")
    timeout_value = os.getenv("LOCAL_API_TIMEOUT") or env_vars.get("TIMEOUT_SECONDS") or "30"
    timeout_seconds = float(timeout_value)

    if not api_key or not base_url:
        pytest.skip("Local API tests require API_KEY/BASE_URL (or LOCAL_API_KEY/LOCAL_API_BASE_URL).")

    return LocalApiConfig(api_key=api_key, base_url=base_url, timeout_seconds=timeout_seconds)


@pytest.fixture(scope="session")
def local_auth_headers(local_api_config: LocalApiConfig) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {local_api_config.api_key}",
        "Content-Type": "application/json",
    }


@pytest_asyncio.fixture
async def local_client(local_api_config: LocalApiConfig) -> AsyncClient:
    async with AsyncClient(base_url=local_api_config.base_url, timeout=local_api_config.timeout_seconds) as client:
        yield client
