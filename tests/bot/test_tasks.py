from unittest.mock import MagicMock, patch

from src.bot.tasks import HOUR_INTERVAL, start_bigclock_scheduler


def test_start_bigclock_scheduler_creates_single_task_when_running():
    bot = MagicMock()
    first_task = MagicMock()
    first_task.done.return_value = False

    state = {"scheduled_coroutines": 0}

    def _create_task(coro):
        # The event loop is mocked in this unit test, so close the coroutine
        # to avoid un-awaited coroutine warnings in teardown.
        state["scheduled_coroutines"] += 1
        coro.close()
        return first_task

    bot.loop.create_task.side_effect = _create_task

    with patch("src.bot.tasks.tick_modulo_scheduler") as mock_tick:
        task_one = start_bigclock_scheduler(bot)
        task_two = start_bigclock_scheduler(bot)

    assert task_one is first_task
    assert task_two is first_task
    mock_tick.assert_called_once_with(bot, period_seconds=HOUR_INTERVAL)
    assert state["scheduled_coroutines"] == 1
    bot.loop.create_task.assert_called_once()


def test_start_bigclock_scheduler_recreates_task_when_finished():
    bot = MagicMock()
    finished_task = MagicMock()
    finished_task.done.return_value = True
    fresh_task = MagicMock()
    fresh_task.done.return_value = False

    state = {"scheduled_coroutines": 0}

    def _create_task(coro):
        # The event loop is mocked in this unit test, so close the coroutine
        # to avoid un-awaited coroutine warnings in teardown.
        state["scheduled_coroutines"] += 1
        coro.close()
        return fresh_task

    bot._bigclock_scheduler_task = finished_task
    bot.loop.create_task.side_effect = _create_task

    with patch("src.bot.tasks.tick_modulo_scheduler") as mock_tick:
        new_task = start_bigclock_scheduler(bot)

    assert new_task is fresh_task
    mock_tick.assert_called_once_with(bot, period_seconds=HOUR_INTERVAL)
    assert state["scheduled_coroutines"] == 1
    bot.loop.create_task.assert_called_once()
