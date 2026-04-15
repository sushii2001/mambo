import pytest
from unittest.mock import MagicMock, patch
from src.bot.handlers import EventHandlers


@pytest.fixture
def event_handlers(bot):
    """Create EventHandlers cog instance"""
    return EventHandlers(bot)


class TestOnMessage:
    """Test message event handler"""

    @pytest.mark.asyncio
    async def test_ignores_bot_messages(self, event_handlers, mock_message):
        """Test that bot ignores messages from other bots"""
        mock_message.author.bot = True

        # on trigger of `on_message`
        result = await event_handlers.on_message(mock_message)

        # Should return early without processing
        assert result is None

    @pytest.mark.asyncio
    async def test_processes_user_messages(self, event_handlers, mock_message):
        """Test that bot processes messages from users"""
        mock_message.author.bot = False
        mock_message.content = "Hello bot!"

        calls = {"process_commands": 0}

        async def _process_commands(_message):
            calls["process_commands"] += 1

        # check the logger `debug`
        with patch.object(event_handlers.bot, "process_commands", new=_process_commands):
            # Should log the message
            with patch.object(event_handlers.bot.logger, 'debug') as mock_log:
                await event_handlers.on_message(mock_message)
                mock_log.assert_called()
                assert calls["process_commands"] == 1

                call_args = str(mock_log.call_args)
                # verify that the test message is in the logger
                assert 'Hello bot!' in call_args


class TestOnMemberJoin:
    """Test member join event handler"""

    @pytest.mark.asyncio
    async def test_logs_new_member(self, event_handlers):
        """Test that member join is logged"""
        mock_member = MagicMock()
        mock_member.__str__ = MagicMock(return_value="NewUser#1234")

        # check logger `info`
        with patch.object(event_handlers.bot.logger, 'info') as mock_log:
            # on trigger of `on_message_join`
            await event_handlers.on_member_join(mock_member)

            mock_log.assert_called_once()
            call_args = str(mock_log.call_args)

            # verify that the new user is in the logger
            assert 'NewUser#1234' in call_args


class TestOnError:
    """Test error event handler"""

    @pytest.mark.asyncio
    async def test_logs_errors(self, event_handlers):
        """Test that errors are logged"""
        test_event = "test_event"

        # check logger `error`
        with patch.object(event_handlers.bot.logger, 'error') as mock_log:
            # on trigger of `on_error`
            await event_handlers.on_error(test_event)

            mock_log.assert_called_once()
            call_args = str(mock_log.call_args)

            # verify that the test event is in the logger
            assert test_event in call_args