

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Define project paths
PROJ_TEST_PATH = Path(__file__).parent
PROJ_ROOT_PATH = PROJ_TEST_PATH.parent

# Add src to Python path
sys.path.insert(0, str(PROJ_ROOT_PATH))

# Set test environment variables BEFORE importing anything
os.environ['DISCORD_TOKEN'] = 'test_token_for_pytest_12345'
os.environ['LOGGING_LEVEL'] = 'DEBUG'
os.environ['COMMAND_PREFIX'] = '!'

from src.bot.client import MamboBot

@pytest.fixture
def bot():
    """
    Fixture to create a bot instance for testing.
    This bot is NOT connected to Discord.
    """
    bot_instance = MamboBot()
    yield bot_instance
    # Cleanup after test if needed

@pytest.fixture
def mock_discord_token(monkeypatch):
    """Fixture to mock Discord token"""
    token = 'mock_token_for_specific_test'
    monkeypatch.setenv('DISCORD_TOKEN', token)
    return token

@pytest.fixture
def mock_ctx():
    """Mock Discord context for command testing"""
    ctx = MagicMock()
    ctx.send = AsyncMock()
    ctx.author = MagicMock()
    ctx.author.name = "TestUser"
    ctx.guild = MagicMock()
    ctx.guild.name = "TestGuild"
    return ctx

@pytest.fixture
def mock_interaction():
    """Mock Discord interaction for slash command testing"""
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.user = MagicMock()
    interaction.user.name = "TestUser"
    interaction.user.mention = "<@123456789>"
    return interaction

@pytest.fixture
def mock_message():
    """Mock Discord message"""
    message = MagicMock()
    message.author = MagicMock()
    message.author.bot = False
    message.author.name = "TestUser"
    message.content = "Test message"
    message.channel = MagicMock()
    message.channel.send = AsyncMock()
    return message