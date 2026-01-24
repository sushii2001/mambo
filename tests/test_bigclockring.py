# tests/test_bigclockring.py
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from src import main

def test_run_bigclockring_creates_task():
    """Test that run_bigclockring creates a task with tick_modulo_scheduler"""

    mock_loop = MagicMock()

    # Create a mock coroutine to avoid unawaited coroutine warnings
    mock_coro = MagicMock()
    mock_coro.__await__ = MagicMock(return_value=iter([]))

    mock_scheduler = MagicMock(return_value=mock_coro)

    with patch.object(main.bot, 'loop', mock_loop), \
        patch('src.main.tick_modulo_scheduler', mock_scheduler):

        main.run_bigclockring()

        # Verify tick_modulo_scheduler is called with correct arguments
        mock_scheduler.assert_called_once_with(main.bot, period_seconds=main.HOUR_INTERVAL)

        # Verify create_task is called once with a coroutine
        mock_loop.create_task.assert_called_once_with(mock_coro)

@pytest.mark.asyncio
async def test_setup_hook_calls_run_bigclockring():
    """Test that setup_hook calls run_bigclockring"""

    with patch('src.main.run_bigclockring') as mock_run_bigclockring:

        await main.setup_hook()

        mock_run_bigclockring.assert_called_once()