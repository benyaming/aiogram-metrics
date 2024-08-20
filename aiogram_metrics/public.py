import asyncio
import inspect
import logging
from typing import Optional

from aiogram.types import Message, CallbackQuery, Update

from aiogram_metrics.api import handle_event
from aiogram_metrics.hub import Hub


def track(arg=None):
    """
    Decorator for saving events. Can be used either with or without an argument.
    If an argument is not provided, message text or callback data will be extracted.
    :param arg: Event name for tracking
    """
    _func = None

    if arg and callable(arg):
        _func = arg
        event = None
    else:
        event = arg

    def decorator(func):

        async def wrapper(*args, **kwargs):
            update = kwargs.get('event_update')

            # Extract argument names
            sig = inspect.signature(func)
            kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

            if not update:
                logging.info(f"No update found for event '{event}', skipping...")
            else:
                if Hub.is_activated:
                    try:
                        coro = handle_event(event, update=update)
                        asyncio.create_task(coro)
                    except Exception as e:
                        logging.error(f"Failed to handle event: {e}")
                else:
                    logging.warning('aiogram-metrics is not registered!')

            if not asyncio.iscoroutinefunction(func):
                async def async_wrapper():
                    return await func(*args, **kwargs)
                return await async_wrapper()
            else:
                return await func(*args, **kwargs)

        return wrapper

    return decorator(_func) if _func else decorator


def manual_track(
    event: Optional[str] = None,
    *,
    update: Optional[Update] = None,
    message: Optional[Message] = None,
    callback_query: Optional[CallbackQuery] = None,
    user_id: Optional[int] = None,
):
    """
    Manual event tracking. Sane as `track` decorator
    """
    coro = handle_event(event, update=update, message=message, callback_query=callback_query, user_id=user_id)
    asyncio.create_task(coro)
