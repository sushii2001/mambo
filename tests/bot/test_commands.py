import discord
import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, PropertyMock, patch
from src.bot.commands import BasicCommands
from src.bot.tasks import BIG_CLOCK_LIST_EN, BIG_CLOCK_RING_PATH, BIG_CLOCK_PERIOD


@pytest.fixture
def basic_commands(bot):
    """Create BasicCommands cog instance"""
    return BasicCommands(bot)

class TestPingCommand:
    """Test ping command"""

    @pytest.mark.asyncio
    async def test_ping_responds(self, basic_commands, mock_ctx):
        with patch.object(type(basic_commands.bot), 'latency', new_callable=PropertyMock, return_value=0.05):
            await basic_commands.ping.callback(basic_commands, mock_ctx)  # ← .callback(self, ctx)

        mock_ctx.send.assert_called_once()
        sent_msg = mock_ctx.send.call_args.args[0]
        assert "Pong!" in sent_msg
        assert "50ms" in sent_msg

@pytest.fixture
def mock_interaction():
    class _SendMessageRecorder:
        def __init__(self):
            self.calls = []

        async def __call__(self, *args, **kwargs):
            self.calls.append((args, kwargs))

        def assert_called_once(self):
            assert len(self.calls) == 1

        @property
        def call_args(self):
            if not self.calls:
                raise AssertionError("send_message was not called")
            args, kwargs = self.calls[-1]
            return SimpleNamespace(args=args, kwargs=kwargs)

    interaction = MagicMock()
    interaction.user.mention = "@TestUser"
    interaction.response.send_message = _SendMessageRecorder()
    return interaction

class TestHelloSlashCommand:
    """Test hello slash command"""

    @pytest.mark.asyncio
    async def test_hello_responds(self, basic_commands, mock_interaction):
        await basic_commands.hello.callback(basic_commands, mock_interaction)  # ← .callback(self, interaction)

        mock_interaction.response.send_message.assert_called_once()
        sent_msg = mock_interaction.response.send_message.call_args.args[0]
        assert "Hello" in sent_msg
        assert "@TestUser" in sent_msg


@pytest.fixture
def reset_big_clock_state():
    BIG_CLOCK_LIST_EN.clear()
    yield
    BIG_CLOCK_LIST_EN.clear()


class TestSetBigClockSlashCommand:
    """Test setbigclock slash command"""

    @pytest.mark.asyncio
    async def test_setbigclock_dm_rejected(
        self, basic_commands, mock_interaction, reset_big_clock_state
    ):
        mock_interaction.guild = None

        await basic_commands.setbigclock.callback(basic_commands, mock_interaction, True)

        mock_interaction.response.send_message.assert_called_once()
        sent_msg = mock_interaction.response.send_message.call_args.args[0]
        assert "server" in sent_msg.lower()
        assert (
            mock_interaction.response.send_message.call_args.kwargs.get("ephemeral")
            is True
        )

    @pytest.mark.asyncio
    async def test_setbigclock_requires_voice_channel(
        self, basic_commands, mock_interaction, reset_big_clock_state
    ):
        mock_interaction.guild = MagicMock(id=1234)

        with patch("src.bot.commands.get_interaction_voice_channel", return_value=None):
            await basic_commands.setbigclock.callback(
                basic_commands, mock_interaction, True
            )

        mock_interaction.response.send_message.assert_called_once()
        sent_msg = mock_interaction.response.send_message.call_args.args[0]
        assert "voice channel" in sent_msg.lower()
        assert (
            mock_interaction.response.send_message.call_args.kwargs.get("ephemeral")
            is True
        )

    @pytest.mark.asyncio
    async def test_setbigclock_enable_true_updates_state(
        self, basic_commands, mock_interaction, reset_big_clock_state
    ):
        guild_id = 4321
        channel_id = 555

        mock_interaction.guild = MagicMock(id=guild_id)
        mock_channel = MagicMock(id=channel_id)

        with patch(
            "src.bot.commands.get_interaction_voice_channel", return_value=mock_channel
        ):
            await basic_commands.setbigclock.callback(
                basic_commands, mock_interaction, True
            )

        assert guild_id in BIG_CLOCK_LIST_EN
        assert BIG_CLOCK_LIST_EN[guild_id]["channel_id"] == channel_id
        assert BIG_CLOCK_LIST_EN[guild_id]["audio_path"] == BIG_CLOCK_RING_PATH
        assert BIG_CLOCK_LIST_EN[guild_id]["seconds"] == BIG_CLOCK_PERIOD
        assert BIG_CLOCK_LIST_EN[guild_id]["enable"] is True

        mock_interaction.response.send_message.assert_called_once()
        sent_msg = mock_interaction.response.send_message.call_args.args[0]
        assert "set big clock" in sent_msg.lower()
        assert "true" in sent_msg.lower()

    @pytest.mark.asyncio
    async def test_setbigclock_enable_false_keeps_entry(
        self, basic_commands, mock_interaction, reset_big_clock_state
    ):
        guild_id = 5678
        channel_id = 777

        BIG_CLOCK_LIST_EN[guild_id] = {
            "channel_id": 1,
            "audio_path": "old-path.mp3",
            "seconds": 99,
            "enable": True,
        }

        mock_interaction.guild = MagicMock(id=guild_id)
        mock_channel = MagicMock(id=channel_id)

        with patch(
            "src.bot.commands.get_interaction_voice_channel", return_value=mock_channel
        ):
            await basic_commands.setbigclock.callback(
                basic_commands, mock_interaction, False
            )

        assert guild_id in BIG_CLOCK_LIST_EN
        assert BIG_CLOCK_LIST_EN[guild_id]["channel_id"] == channel_id
        assert BIG_CLOCK_LIST_EN[guild_id]["audio_path"] == BIG_CLOCK_RING_PATH
        assert BIG_CLOCK_LIST_EN[guild_id]["seconds"] == BIG_CLOCK_PERIOD
        assert BIG_CLOCK_LIST_EN[guild_id]["enable"] is False

        mock_interaction.response.send_message.assert_called_once()
        sent_msg = mock_interaction.response.send_message.call_args.args[0]
        assert "set big clock" in sent_msg.lower()
        assert "false" in sent_msg.lower()