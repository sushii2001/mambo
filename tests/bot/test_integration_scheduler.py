import discord
import pytest
from unittest.mock import MagicMock, patch

from src.bot.tasks import (
    BIG_CLOCK_LIST_EN,
    BIG_CLOCK_PERIOD,
    BIG_CLOCK_RING_PATH,
    HOUR_INTERVAL,
    tick_modulo_scheduler,
)


async def _fake_sleep(_seconds: float):
    return None


@pytest.fixture
def reset_big_clock_state():
    BIG_CLOCK_LIST_EN.clear()
    yield
    BIG_CLOCK_LIST_EN.clear()


@pytest.mark.asyncio
async def test_tick_scheduler_boundary_joins_plays_disconnects(reset_big_clock_state):
    bot = MagicMock()
    state = {
        "wait_until_ready": 0,
        "connect": 0,
        "disconnect": 0,
        "wait_play_done": [],
    }

    async def _wait_until_ready():
        state["wait_until_ready"] += 1

    bot.wait_until_ready = _wait_until_ready
    bot.is_closed.side_effect = [False, True]

    guild_id = 9876
    channel_id = 5432

    guild = MagicMock(id=guild_id)
    channel = MagicMock(spec=discord.VoiceChannel)
    channel.id = channel_id

    voice_client = MagicMock(spec=discord.VoiceClient)
    voice_client.is_connected.return_value = True
    async def _disconnect():
        state["disconnect"] += 1

    voice_client.disconnect = _disconnect

    async def _connect():
        state["connect"] += 1
        return voice_client

    channel.connect = _connect

    guild.voice_client = None
    guild.get_channel.return_value = channel
    bot.get_guild.return_value = guild

    BIG_CLOCK_LIST_EN[guild_id] = {
        "channel_id": channel_id,
        "audio": BIG_CLOCK_RING_PATH,
        "audio_path": BIG_CLOCK_RING_PATH,
        "seconds": BIG_CLOCK_PERIOD,
        "enable": True,
    }

    async def _wait_play_done(vc, *, max_seconds=None):
        state["wait_play_done"].append((vc, max_seconds))

    with patch("src.bot.tasks.time.time", side_effect=[0, HOUR_INTERVAL + 1]), patch(
        "src.bot.tasks.asyncio.sleep", new=_fake_sleep
    ), patch("src.bot.voice.make_ffmpeg_source", return_value=MagicMock()) as mock_src, patch(
        "src.bot.voice.play_audio"
    ) as mock_play, patch("src.bot.voice.wait_play_done", new=_wait_play_done):
        await tick_modulo_scheduler(bot, period_seconds=HOUR_INTERVAL)

    assert state["wait_until_ready"] == 1
    assert state["connect"] == 1
    mock_src.assert_called_once_with(BIG_CLOCK_RING_PATH)
    mock_play.assert_called_once()
    assert state["wait_play_done"] == [(voice_client, BIG_CLOCK_PERIOD)]
    assert state["disconnect"] == 1


@pytest.mark.asyncio
async def test_tick_scheduler_skips_disabled_entry(reset_big_clock_state):
    bot = MagicMock()
    async def _wait_until_ready():
        return None

    bot.wait_until_ready = _wait_until_ready
    bot.is_closed.side_effect = [False, True]

    guild_id = 555
    guild = MagicMock(id=guild_id)
    bot.get_guild.return_value = guild

    BIG_CLOCK_LIST_EN[guild_id] = {
        "channel_id": 1,
        "audio_path": BIG_CLOCK_RING_PATH,
        "seconds": BIG_CLOCK_PERIOD,
        "enable": False,
    }

    with patch("src.bot.tasks.time.time", side_effect=[0, HOUR_INTERVAL + 1]), patch(
        "src.bot.tasks.asyncio.sleep", new=_fake_sleep
    ):
        await tick_modulo_scheduler(bot, period_seconds=HOUR_INTERVAL)

    guild.get_channel.assert_not_called()
