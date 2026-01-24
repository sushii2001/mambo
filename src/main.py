#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import datetime as dt
from zoneinfo import ZoneInfo
import time
import logging

# Load project envs
load_dotenv()
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

# Define project paths
PROJ_SRC_PATH = os.path.dirname(os.path.abspath(__file__))
PROJ_ROOT_PATH = f"{PROJ_SRC_PATH}/../"
PROJ_LOG_PATH = f"{PROJ_ROOT_PATH}/logs"
DISCORD_LOG_PATH = f"{PROJ_LOG_PATH}/discord.log"

# Append project repo into python module for relative imports
sys.path.append(PROJ_SRC_PATH)
from webserver import keep_alive

# Bot initialization
os.makedirs(PROJ_LOG_PATH, exist_ok=True)
log_handler = logging.FileHandler(filename=DISCORD_LOG_PATH, encoding="utf-8", mode="w")
logger = logging.getLogger("discord_logger")
logger.addHandler(log_handler)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Tools initialization
BIG_CLOCK_LIST_EN: dict[int, dict] = {}
BIG_CLOCK_PERIOD = 9
BIG_CLOCK_RING_PATH = f"{PROJ_ROOT_PATH}/asset/audio/tracks/bigclockring.mp3"
HOUR_INTERVAL = 3600
TZ = ZoneInfo("Asia/Kuala_Lumpur")

# Local develop configuration
DUMMY_ROLE = "Dummy"
LOGGING_LEVEL = logging.ERROR
logger.setLevel(LOGGING_LEVEL)

# ---------- Events ----------
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Connected to {len(bot.guilds)} guilds')
    print('Syncing commands...')
    await bot.tree.sync()
    print('Commands synced!')
    print(f"We are ready to go in, {bot.user.name}!")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.event
async def on_message(message):
    # skip message from bot itsef
    if message.author == bot.user:
        return

    # profanity check
    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - That's not very sigma. 🙂")

    logger.debug(f"Message received: {message.content}")
    # discord original handling
    await bot.process_commands(message)

@bot.event
async def setup_hook():
    """
    Create tasks that runs periodically if enabled
    """
    run_bigclockring()

# ---------- Interactions ----------
@bot.tree.command(name="test123", description="Testing 123")
async def test123(interaction: discord.Interaction):
    await interaction.response.send_message(f"Testing 123 ... from {interaction.user.mention}!")

@bot.tree.command(name="setbigclock", description="Set big clock to ring")
async def setbigclock(interaction: discord.Interaction, enable: bool):
    set_result = True
    if interaction.guild:
        ch = get_interaction_voice_channel(interaction)
        if not ch: set_result = False

    if set_result:
        BIG_CLOCK_LIST_EN[interaction.guild.id] = {
            "channel_id": ch.id,
            "audio": BIG_CLOCK_RING_PATH,
            "seconds": float(BIG_CLOCK_PERIOD),
            "enable": enable,
        }
        await interaction.response.send_message(f"Set Big Clock is {enable} from {interaction.user.mention}!")
    else:
        await interaction.response.send_message(f"Set Big Clock is FAILED, ensure you are in a voice channel")


# ---------- Commands ----------
@bot.command(name="hello", description="Says hello back!")
async def hello(ctx):
    # !hello
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=DUMMY_ROLE)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {role} role!")
    else:
        await ctx.send(f"Role {role} doesn't exist")

@bot.command()
async def remove_role(ctx):
    role = discord.utils.get(ctx.guild.roles, name=DUMMY_ROLE)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention}'s {role} role is now removed!")
    else:
        await ctx.send(f"Role {role} doesn't exist")

@bot.command()
@commands.has_role(DUMMY_ROLE)
async def secret(ctx):
    await ctx.send(f"Welcome to the {DUMMY_ROLE} club 🤡")

@secret.error
async def secret_err(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"You're not part of the hood little bro 🗿")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"Message from {ctx.author}:\n {msg}")

@bot.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message!")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_msg = await ctx.send(embed=embed)
    await poll_msg.add_reaction("👍")
    await poll_msg.add_reaction("👎")

@bot.command()
async def join(ctx: commands.Context):
    # !join
    # Joins same voice channel as user (user must be in voice channel)
    ch = await get_user_voice_channel(ctx)
    if not ch:
        return
    await ensure_voice_connected(ctx, channel=ch)

@bot.command()
async def leave(ctx: commands.Context):
    await disconnect_voice(ctx)

@bot.command()
async def play(ctx: commands.Context, url_or_path: str):
    # Plays full file/stream, stays connected.
    await join_play_leave(
        ctx,
        audio_url_or_path=url_or_path,
        play_seconds=None,
        disconnect_when_done=False,
    )

# ---------- Voice Helpers (generic, reusable) ----------
FFMPEG = "/usr/bin/ffmpeg"

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
    if ctx.guild is None:
        raise RuntimeError("Voice is only supported in guilds.")

    vc = ctx.voice_client
    if vc and vc.is_connected():
        return vc

    if channel is None:
        channel = await get_user_voice_channel(ctx)
    if channel is None:
        raise RuntimeError("No target voice channel.")

    return await asyncio.wait_for(channel.connect(), timeout=timeout)

async def get_user_voice_channel(ctx: commands.Context) -> discord.VoiceChannel | None:
    """Return the voice channel the command author is currently in."""
    try:
        v = getattr(ctx.author, "voice", None)
        return v.channel if v and v.channel else None
    except Exception as e:
        logger.error(f"Could not get user voice channel: {e}")
        return None

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

# ---------- Tasks ----------
def run_bigclockring():
    bot.loop.create_task(tick_modulo_scheduler(bot, period_seconds=HOUR_INTERVAL))

# ---------- Tasks Helpers (generic, reusable) ----------
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

                source = make_ffmpeg_source(cfg["audio"])

                play_audio(vc, source)

                await wait_play_done(vc, max_seconds=cfg["seconds"])
                if vc.is_connected():
                    await vc.disconnect()
            except Exception as e:
                logger.error(f"Something went wrong during tick {str(e)}")
                continue

# ---------- Main ----------
def main():
    try:
        keep_alive()
        bot.run(DISCORD_TOKEN, log_handler=log_handler, log_level=LOGGING_LEVEL)
    except KeyboardInterrupt:
        logger.debug(f"Bot stopped manually.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()