from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient


@dataclass(frozen=True)
class LiveApiConfig:
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
def live_api_config() -> LiveApiConfig:
    if os.getenv("LIVE_API_TESTS", "").lower() != "true":
        pytest.skip("Live API tests disabled. Set LIVE_API_TESTS=true to run.")

    env_path = Path(__file__).with_name(".env.prod")
    env_vars = _load_env_file(env_path)

    api_key = os.getenv("LIVE_API_KEY") or os.getenv("API_KEY") or env_vars.get("API_KEY")
    base_url = os.getenv("LIVE_API_BASE_URL") or os.getenv("BASE_URL") or env_vars.get("BASE_URL")
    timeout_seconds = float(os.getenv("LIVE_API_TIMEOUT", "30"))

    if not api_key or not base_url:
        pytest.skip("Live API tests require API_KEY/BASE_URL (or LIVE_API_KEY/LIVE_API_BASE_URL).")

    return LiveApiConfig(api_key=api_key, base_url=base_url, timeout_seconds=timeout_seconds)


@pytest.fixture(scope="session")
def live_auth_headers(live_api_config: LiveApiConfig) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {live_api_config.api_key}",
        "Content-Type": "application/json",
    }


@pytest_asyncio.fixture
async def live_client(live_api_config: LiveApiConfig) -> AsyncClient:
    async with AsyncClient(base_url=live_api_config.base_url, timeout=live_api_config.timeout_seconds) as client:
        yield client
