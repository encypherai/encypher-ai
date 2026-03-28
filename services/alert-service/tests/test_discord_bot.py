"""Tests for Discord bot slash commands."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestBotCommands:
    """Test that bot builds and commands are registered."""

    def test_build_bot_creates_command_tree(self):
        from app.services.discord_bot import _build_bot

        bot = _build_bot()
        # Verify the tree has commands registered
        assert bot.tree is not None
        command_names = [c.name for c in bot.tree.get_commands()]
        assert "status" in command_names
        assert "incidents" in command_names
        assert "investigate" in command_names
        assert "ack" in command_names
        assert "resolve" in command_names
        assert "patterns" in command_names

    @pytest.mark.asyncio
    async def test_start_skips_without_token(self):
        with patch("app.services.discord_bot.settings") as mock_settings:
            mock_settings.DISCORD_BOT_TOKEN = ""
            from app.services.discord_bot import start_discord_bot

            await start_discord_bot()
            # Should not raise, just skip

    @pytest.mark.asyncio
    async def test_stop_handles_no_bot(self):
        from app.services.discord_bot import stop_discord_bot

        # Should not raise when no bot is running
        await stop_discord_bot()
