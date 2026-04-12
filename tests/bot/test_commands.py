import discord
import pytest
from unittest.mock import MagicMock, AsyncMock, PropertyMock, patch
from src.bot.commands import BasicCommands


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
    interaction = MagicMock(spec=discord.Interaction)
    interaction.user.mention = "@TestUser"
    interaction.response.send_message = AsyncMock()  # ← must be AsyncMock
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