import pytest
import discord
from discord.ext import commands
from unittest.mock import MagicMock, patch
from src.bot.client import MamboBot
from src.utils.config import Config


class TestBotInitialization:
    """Test bot setup and configuration"""

    def test_bot_is_commands_bot_instance(self, bot):
        """Test that bot is an instance of commands.Bot"""
        assert isinstance(bot, commands.Bot)
        assert isinstance(bot, MamboBot)

    def test_bot_intents(self, bot):
        """Test that bot has correct intents configured"""
        assert bot.intents.message_content is True
        assert bot.intents.guilds is True
        assert bot.intents.members is True

    def test_bot_command_prefix(self, bot):
        """Test that bot has correct command prefix"""
        assert bot.command_prefix == Config.COMMAND_PREFIX

    def test_bot_tree_exists(self, bot):
        """Test that command tree exists for slash commands"""
        assert bot.tree is not None
        assert isinstance(bot.tree, discord.app_commands.CommandTree)

class TestBotLogger:
    """Test logging configuration"""

    def test_bot_has_logger(self, bot):
        """Test that bot logger is properly initialized"""
        assert bot.logger is not None
        assert bot.logger.name == "discord_logger"

    def test_logger_level(self, bot):
        """Test logger is set to correct level"""
        assert bot.logger.level == Config.LOGGING_LEVEL

    def test_logger_has_handlers(self, bot):
        """Test that logger has both file and console handlers"""
        assert len(bot.logger.handlers) >= 2

        handler_types = [type(h).__name__ for h in bot.logger.handlers]
        # Check for file handler (either regular or rotating)
        has_file_handler = any(
            h in handler_types
            for h in ['FileHandler', 'RotatingFileHandler']
        )
        assert has_file_handler, f"No file handler found. Handlers: {handler_types}"
        assert 'StreamHandler' in handler_types, f"No console handler found. Handlers: {handler_types}"

    def test_logger_propagate_is_false(self, bot):
        """Test that logger doesn't propagate to root logger"""
        assert bot.logger.propagate is False

class TestBotLifecycle:
    """Test bot startup and shutdown"""

    @pytest.mark.asyncio
    async def test_load_commands_uses_package_qualified_extension(self, bot):
        loaded_extensions = []

        async def _load_extension(extension_name):
            loaded_extensions.append(extension_name)

        with patch.object(bot, 'load_extension', new=_load_extension):
            await bot.load_commands()

        assert loaded_extensions == ["src.bot.commands"]

    @pytest.mark.asyncio
    async def test_load_commands_fail_fast_on_extension_error(self, bot):
        async def _load_extension(_extension_name):
            raise RuntimeError("load failure")

        with patch.object(bot, 'load_extension', new=_load_extension), \
            patch.object(bot.logger, 'error') as mock_error, \
            pytest.raises(RuntimeError):

            await bot.load_commands()

        mock_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_setup_hook_initialization(self, bot):
        calls = {"load": 0, "sync": 0}

        async def _load_commands():
            calls["load"] += 1

        async def _sync_tree(*_args, **_kwargs):
            calls["sync"] += 1

        with patch.object(bot, 'load_commands', new=_load_commands), \
            patch.object(bot.tree, 'sync', new=_sync_tree), \
            patch('src.bot.client.start_bigclock_scheduler') as mock_start_scheduler:

            await bot.setup_hook()

            # check if `load_commands` is triggered
            assert calls["load"] == 1
            # check if sync commands is triggered
            assert calls["sync"] == 1
            # check if scheduler startup is triggered
            mock_start_scheduler.assert_called_once_with(bot)

    @pytest.mark.asyncio
    async def test_on_ready_logs_username(self, bot):
        """Test that on_ready logs bot username"""
        # Create a mock for the bot user object
        test_botname = "TestBot#1234"
        mock_user  = MagicMock()
        mock_user.__str__ = lambda self:test_botname

        bot._connection.user = mock_user
        bot._connection._guilds = {}

        with patch.object(bot.logger, 'info') as mock_log:

            await bot.on_ready()

            log_outputs = [call.args[0] for call in mock_log.call_args_list if call.args]
            assert any(test_botname in msg for msg in log_outputs), \
                f"Expected username in logs, got: {log_outputs}"

    @pytest.mark.asyncio
    async def test_on_ready_logs_guild_count(self, bot):
        """Test that on_ready logs number of guilds"""
        # Create a mock for the bot user object
        test_botname = "TestBot#1234"
        # define test 3 example guilds
        num_guilds = 3
        mock_user  = MagicMock()
        mock_user.__str__ = lambda self:test_botname
        mock_guilds = []
        for idx in range(num_guilds):
            guild = MagicMock()
            guild.id = idx + 1
            guild.name = f"Guild-{idx + 1}"
            mock_guilds.append(guild)

        bot._connection.user = mock_user
        bot._connection._guilds = {guild.id: guild for guild in mock_guilds}

        with patch.object(bot.logger, 'info') as mock_log:

            await bot.on_ready()

            log_outputs = [call.args[0] for call in mock_log.call_args_list if call.args]
            assert any(str(num_guilds) in msg and 'guild' in msg for msg in log_outputs), \
                f"Expected guild count in logs, got: {log_outputs}"

class TestBotErrorHandling:
    """Test error handling in run_bot"""

    def test_run_bot_handles_keyboard_interrupt(self, bot):
        """Test that KeyboardInterrupt is handled gracefully"""
        with patch.object(bot, 'run', side_effect=KeyboardInterrupt):
            with patch.object(bot.logger, 'info') as mock_log:
                bot.run_bot()

                # Should log manual stop
                assert any(
                    'stopped manually' in str(call).lower()
                    for call in mock_log.call_args_list
                )

    def test_run_bot_handles_generic_exception(self, bot):
        """Test that unexpected exceptions are logged as critical"""
        test_error = Exception("Test error")

        with patch.object(bot, 'run', side_effect=test_error), \
            patch.object(bot.logger, 'critical') as mock_critical:
            bot.run_bot()
            mock_critical.assert_called()

    def test_run_bot_handles_keyboard_interrupt(self, bot):
        with patch.object(bot, 'run', side_effect=KeyboardInterrupt()), \
            patch.object(bot.logger, 'info') as mock_info:
            bot.run_bot()
            log_outputs = [call.args[0] for call in mock_info.call_args_list if call.args]
            assert any("Bot stopped manually" in msg for msg in log_outputs)

    def test_run_bot_handles_login_failure(self, bot):
        with patch.object(bot, 'run', side_effect=discord.LoginFailure()), \
            patch.object(bot.logger, 'critical') as mock_critical:
            bot.run_bot()
            mock_critical.assert_called()

    def test_run_bot_handles_http_exception(self, bot):
        with patch.object(bot, 'run', side_effect=discord.HTTPException(MagicMock(), "HTTP error")), \
            patch.object(bot.logger, 'error') as mock_error:
            bot.run_bot()
            mock_error.assert_called()

    def test_run_bot_always_logs_shutdown(self, bot):
        """Test that finally block always runs"""
        with patch.object(bot, 'run'), \
            patch.object(bot.logger, 'info') as mock_info:
            bot.run_bot()
            log_outputs = [call.args[0] for call in mock_info.call_args_list if call.args]
            assert any("shutdown" in msg for msg in log_outputs)