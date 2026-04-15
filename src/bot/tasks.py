import discord
from discord.ext import commands
import asyncio
import datetime as dt
import time
import logging
from src.utils.config import Config

logger = logging.getLogger("discord_logger")

BIG_CLOCK_PERIOD = Config.BIG_CLOCK_PERIOD
BIG_CLOCK_RING_PATH = "assets/audio/tracks/bigclockring.mp3"  # relative to project root
HOUR_INTERVAL = Config.HOUR_INTERVAL


def start_bigclock_scheduler(bot: commands.Bot):
    """Start scheduler once and reuse existing running task if present."""
    existing_task = getattr(bot, "_bigclock_scheduler_task", None)
    if existing_task and not existing_task.done():
        return existing_task

    task = bot.loop.create_task(
        tick_modulo_scheduler(bot, period_seconds=HOUR_INTERVAL)
    )
    setattr(bot, "_bigclock_scheduler_task", task)
    return task

async def tick_modulo_scheduler(bot: commands.Bot, *, period_seconds: int):
    """
    Every 1 second:
    now = epoch seconds
    if now // period_seconds changed since last tick -> boundary crossed -> fire once
    This avoids double-firing and does not require exact alignment sleep.
    """
    await bot.wait_until_ready()

    last_bucket = int(time.time()) // period_seconds

    while not bot.is_closed():
        await asyncio.sleep(1.0)

        now = int(time.time())
        bucket = now // period_seconds
        if bucket == last_bucket:
            continue
        last_bucket = bucket  # crossed into a new period boundary

        # TODO: enhance to support other enable tasks
        for guild_id, cfg in list(BIG_CLOCK_LIST_EN.items()):
            guild = bot.get_guild(guild_id)
            if not guild or not cfg.get("enable", False):
                continue

            ch = guild.get_channel(cfg["channel_id"])
            if not isinstance(ch, discord.VoiceChannel):
                continue

            try:
                vc = guild.voice_client
                if not (vc and vc.is_connected()):
                    vc = await ch.connect()

                from .voice import make_ffmpeg_source, play_audio, wait_play_done
                audio_path = cfg.get("audio") or cfg.get("audio_path") or BIG_CLOCK_RING_PATH
                source = make_ffmpeg_source(audio_path)

                play_audio(vc, source)

                await wait_play_done(vc, max_seconds=cfg.get("seconds", BIG_CLOCK_PERIOD))
                if vc.is_connected():
                    await vc.disconnect()
            except Exception as e:
                logger.error(f"Something went wrong during tick {str(e)}")
                continue

# Global state (consider moving to a config or state module later)
BIG_CLOCK_LIST_EN: dict[int, dict] = {}