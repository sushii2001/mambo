import discord
from discord.ext import commands
import asyncio
import datetime as dt
import logging

logger = logging.getLogger("discord_logger")

# Constants
FFMPEG = "/usr/bin/ffmpeg"

def get_interaction_voice_channel(
    interaction: discord.Interaction,
) -> discord.VoiceChannel | None:
    if not interaction.guild:
        return None

    member = interaction.user
    if not isinstance(member, discord.Member):
        return None

    if not member.voice or not member.voice.channel:
        return None

    return member.voice.channel

async def int_disconnect_voice(vc: discord.VoiceClient | None) -> bool:
    if vc and vc.is_connected():
        await vc.disconnect()
        return True
    return False

def make_ffmpeg_source(path: str) -> discord.AudioSource:
    return discord.FFmpegPCMAudio(path, executable=FFMPEG)

async def ensure_voice_connected(
    ctx: commands.Context,
    *,
    channel: discord.VoiceChannel | None = None,
    timeout: float = 20.0,
) -> discord.VoiceClient:
    """
    Ensure the bot is connected to a voice channel in this guild.
    - If already connected, returns the existing VoiceClient.
    - If not connected, connects to `channel` or the author's current channel.
    """
    logger.debug(f"Trying to join1")
    if ctx.guild is None:
        logger.error("Voice commands only work in guilds")
        raise RuntimeError("Voice is only supported in guilds.")

    vc = ctx.voice_client
    logger.debug(f"Trying to join2 - Current voice client: {vc}")
    if vc:
        logger.debug(f"Voice client exists - is_connected: {vc.is_connected()}, channel: {vc.channel}")
    else:
        logger.debug("No existing voice client")

    # Check if there's an active connection
    if vc and vc.is_connected():
        logger.debug(f"Already connected to {vc.channel}")
        return vc

    # Disconnect any stale voice clients before reconnecting
    if vc:
        logger.debug("Disconnecting stale voice client")
        try:
            await vc.disconnect(force=True)
            logger.debug("Disconnected stale voice client successfully")
        except Exception as e:
            logger.warning(f"Error disconnecting stale VC: {e}")

    if channel is None:
        logger.debug("No channel provided, getting user's channel")
        channel = await get_user_voice_channel(ctx)
        logger.debug(f"Got user's channel: {channel}")

    if channel is None:
        logger.error("No target voice channel found")
        raise RuntimeError("No target voice channel.")

    logger.debug(f"Connecting to {channel.name}...")
    try:
        vc = await asyncio.wait_for(channel.connect(), timeout=timeout)
        logger.info(f"Successfully connected to voice channel: {channel.name}")
        return vc
    except asyncio.TimeoutError as e:
        logger.error(f"Timeout connecting to {channel.name}: {e}")
        raise
    except discord.Forbidden as e:
        logger.error(f"Permission denied connecting to {channel.name}: {e}")
        raise
    except discord.HTTPException as e:
        logger.error(f"HTTP error connecting to {channel.name}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to {channel.name}: {e}", exc_info=True)
        raise

async def get_user_voice_channel(ctx: commands.Context) -> discord.VoiceChannel | None:
    """Return the voice channel the command author is currently in."""
    try:
        logger.debug(f"Getting voice channel for user: {ctx.author}")
        v = getattr(ctx.author, "voice", None)
        logger.debug(f"User voice attribute: {v}")
        if v and v.channel:
            logger.debug(f"Found voice channel: {v.channel.name} (ID: {v.channel.id})")
            return v.channel
        else:
            logger.debug("User is not in a voice channel")
            return None
    except Exception as e:
        logger.error(f"Could not get user voice channel: {e}", exc_info=True)
        return None

async def disconnect_voice(ctx: commands.Context) -> None:
    """Disconnect bot from voice in this guild (no-op if not connected)."""
    vc = ctx.voice_client
    if vc and vc.is_connected():
        await vc.disconnect()

async def join_play_leave(
    ctx: commands.Context,
    *,
    channel: discord.VoiceChannel | None = None,
    audio_url_or_path: str,
    play_seconds: float | None = None,
    disconnect_when_done: bool = True,
) -> None:
    """
    One-shot utility:
    - connect (or reuse connection)
    - play audio
    - optionally stop after `play_seconds`
    - optionally disconnect
    """
    vc = await ensure_voice_connected(ctx, channel=channel)

    # If this is a URL, FFmpeg can usually handle it if compiled with the right protocols.
    source = make_ffmpeg_source(audio_url_or_path)
    play_audio(vc, source)

    await wait_play_done(vc, max_seconds=play_seconds)

    if disconnect_when_done:
        await disconnect_voice(ctx)

def play_audio(
    vc: discord.VoiceClient,
    source: discord.AudioSource,
    *,
    after_cb=None,
) -> None:
    """
    Start playing audio on an existing VoiceClient.
    `after_cb` is called by discord.py from a different thread.
    """
    if vc.is_playing():
        vc.stop()
    vc.play(source, after=after_cb)

async def wait_play_done(
    vc: discord.VoiceClient,
    *,
    max_seconds: float | None = None,
) -> None:
    """Await until audio playback ends (or max_seconds timeout if provided)."""
    start = dt.datetime.now(dt.timezone.utc)
    while vc.is_connected() and vc.is_playing():
        if max_seconds is not None:
            if (dt.datetime.now(dt.timezone.utc) - start).total_seconds() >= max_seconds:
                vc.stop()
                break
        await asyncio.sleep(0.2)