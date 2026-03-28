"""Discord bot with slash commands for incident management."""

import asyncio
import logging
from typing import Optional

import discord
from discord import app_commands

from ..core.config import settings
from ..db.session import SessionLocal
from .incident_service import classify_severity, get_patterns, get_summary

logger = logging.getLogger(__name__)

_bot: Optional["AlertBot"] = None


class AlertBot(discord.Client):
    """Discord bot for Encypher alert management."""

    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self._ready_event = asyncio.Event()

    async def setup_hook(self):
        if settings.DISCORD_GUILD_ID:
            guild = discord.Object(id=int(settings.DISCORD_GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info("Synced slash commands to guild %s", settings.DISCORD_GUILD_ID)
        else:
            await self.tree.sync()
            logger.info("Synced slash commands globally")

    async def on_ready(self):
        logger.info("Discord bot connected as %s", self.user)
        self._ready_event.set()


def _build_bot() -> AlertBot:
    """Build and configure the bot with all slash commands."""
    bot = AlertBot()

    @bot.tree.command(name="status", description="Current system health summary")
    async def cmd_status(interaction: discord.Interaction):
        await interaction.response.defer()
        db = SessionLocal()
        try:
            summary = get_summary(db)
        finally:
            db.close()

        status_emoji = {"critical": "CRITICAL", "warning": "WARNING", "healthy": "OK"}
        status_label = status_emoji.get(summary["status"], summary["status"])

        embed = discord.Embed(
            title=f"System Status: {status_label} {summary['status'].upper()}",
            color={"critical": 0xFF0000, "warning": 0xFFA500, "healthy": 0x00FF00}.get(summary["status"], 0x808080),
        )
        embed.add_field(name="Open Incidents", value=str(summary["open_count"]), inline=True)
        embed.add_field(name="Critical", value=str(summary["critical_count"]), inline=True)
        embed.add_field(name="Warning", value=str(summary["warning_count"]), inline=True)
        embed.add_field(name="Errors (5m)", value=str(summary["error_rate_last_5m"]), inline=True)
        embed.add_field(name="Trend", value=summary["error_rate_trend"], inline=True)
        embed.add_field(name="New Types (1h)", value=str(summary["new_error_types_last_hour"]), inline=True)

        if summary.get("top_services"):
            svc_list = "\n".join(f"- {s['service']}: {s['count']}" for s in summary["top_services"][:5])
            embed.add_field(name="Top Services", value=svc_list, inline=False)

        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="incidents", description="List open incidents")
    @app_commands.describe(
        status="Filter by status (open/acknowledged/resolved)",
        severity="Filter by severity (critical/warning/info)",
        limit="Number of results (default 10)",
    )
    async def cmd_incidents(
        interaction: discord.Interaction,
        status: Optional[str] = "open",
        severity: Optional[str] = None,
        limit: int = 10,
    ):
        await interaction.response.defer()
        db = SessionLocal()
        try:
            from ..db.models import Incident
            from sqlalchemy import desc

            q = db.query(Incident)
            if status:
                q = q.filter(Incident.status == status)
            if severity:
                q = q.filter(Incident.severity == severity)
            incidents = q.order_by(desc(Incident.last_seen_at)).limit(min(limit, 25)).all()
        finally:
            db.close()

        if not incidents:
            await interaction.followup.send(f"No incidents found (status={status}, severity={severity})")
            return

        lines = []
        for i in incidents:
            age = ""
            if i.last_seen_at:
                age = f" ({i.last_seen_at.strftime('%H:%M')})"
            lines.append(f"**{i.severity.upper()}** `{i.id[:8]}` {i.title[:80]}{age} [{i.occurrence_count}x]")

        embed = discord.Embed(
            title=f"Incidents ({status or 'all'})",
            description="\n".join(lines[:25]),
            color=0x3498DB,
        )
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="investigate", description="Trigger an AI investigation for an incident")
    @app_commands.describe(incident_id="Incident ID (full or prefix)")
    async def cmd_investigate(interaction: discord.Interaction, incident_id: str):
        await interaction.response.defer()
        db = SessionLocal()
        try:
            from ..db.models import Incident

            incident = db.query(Incident).filter(Incident.id.startswith(incident_id)).first()
            if not incident:
                await interaction.followup.send(f"Incident `{incident_id}` not found")
                return

            # Trigger CC investigation
            from .cc_trigger import trigger_investigation

            result = await trigger_investigation(incident, source="discord")

            if result == "triggered":
                await interaction.followup.send(
                    f"Investigation started for `{incident.id[:8]}` - {incident.title[:100]}\n"
                    "Updates will be posted here as the investigation progresses."
                )
            elif result == "no_webhook":
                await interaction.followup.send(
                    f"CC_WEBHOOK_URL not configured. Cannot trigger automated investigation.\n"
                    f"Incident: `{incident.id[:8]}` - {incident.title[:100]}"
                )
            else:
                await interaction.followup.send(f"Failed to trigger investigation: {result}")
        finally:
            db.close()

    @bot.tree.command(name="ack", description="Acknowledge an incident")
    @app_commands.describe(incident_id="Incident ID (full or prefix)")
    async def cmd_ack(interaction: discord.Interaction, incident_id: str):
        db = SessionLocal()
        try:
            from ..db.models import Incident

            incident = db.query(Incident).filter(Incident.id.startswith(incident_id)).first()
            if not incident:
                await interaction.response.send_message(f"Incident `{incident_id}` not found")
                return
            incident.status = "acknowledged"
            db.commit()
            await interaction.response.send_message(f"Acknowledged: `{incident.id[:8]}` - {incident.title[:80]}")
        finally:
            db.close()

    @bot.tree.command(name="resolve", description="Resolve an incident")
    @app_commands.describe(incident_id="Incident ID (full or prefix)")
    async def cmd_resolve(interaction: discord.Interaction, incident_id: str):
        db = SessionLocal()
        try:
            from ..db.models import Incident
            from datetime import datetime

            incident = db.query(Incident).filter(Incident.id.startswith(incident_id)).first()
            if not incident:
                await interaction.response.send_message(f"Incident `{incident_id}` not found")
                return
            incident.status = "resolved"
            incident.resolved_at = datetime.utcnow()
            db.commit()
            await interaction.response.send_message(f"Resolved: `{incident.id[:8]}` - {incident.title[:80]}")
        finally:
            db.close()

    @bot.tree.command(name="patterns", description="Show error patterns and recurring issues")
    async def cmd_patterns(interaction: discord.Interaction):
        await interaction.response.defer()
        db = SessionLocal()
        try:
            data = get_patterns(db)
        finally:
            db.close()

        embed = discord.Embed(title="Error Patterns (24h)", color=0x9B59B6)

        if data.get("services_by_error_rate"):
            svc_lines = "\n".join(f"- {s['service']}: {s['errors_last_hour']} errors/hr" for s in data["services_by_error_rate"][:10])
            embed.add_field(name="Service Error Rates (1h)", value=svc_lines or "None", inline=False)

        if data.get("recurring_errors"):
            err_lines = []
            for e in data["recurring_errors"][:10]:
                err_lines.append(f"`{e['id'][:8]}` {e.get('error_code', 'unknown')} on {e.get('service', '?')} [{e['occurrences']}x]")
            embed.add_field(name="Recurring Errors", value="\n".join(err_lines) or "None", inline=False)

        await interaction.followup.send(embed=embed)

    return bot


async def start_discord_bot() -> None:
    """Start the Discord bot as a background task."""
    global _bot
    if not settings.DISCORD_BOT_TOKEN:
        logger.info("DISCORD_BOT_TOKEN not set, skipping Discord bot")
        return

    _bot = _build_bot()
    asyncio.create_task(_bot.start(settings.DISCORD_BOT_TOKEN))
    logger.info("Discord bot starting...")


async def stop_discord_bot() -> None:
    """Gracefully shut down the Discord bot."""
    global _bot
    if _bot:
        await _bot.close()
        _bot = None
        logger.info("Discord bot stopped")
