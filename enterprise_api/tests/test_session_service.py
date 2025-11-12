import pytest

from app.services.session_service import session_service


@pytest.mark.asyncio
async def test_stream_state_cache_roundtrip():
    run_id = "run-test"
    await session_service.save_stream_state(run_id, {"status": "start"})
    state = await session_service.get_stream_state(run_id)
    assert state is not None
    assert state["status"] == "start"
    await session_service.delete_stream_state(run_id)
    assert await session_service.get_stream_state(run_id) is None
