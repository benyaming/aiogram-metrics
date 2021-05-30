import asyncio
import inspect

from aiogram_metrics.api import handle_event


def track(arg):
    """
    Decorator for saving events. Could be used either with argument and not.
    If argument is not provided, message text or callback data will be extracted.
    :param arg: Event name for tracking
    """
    _func = None

    if arg and callable(arg):
        _func = arg

    if _func:
        event = None

    if not _func:
        event = arg

    def decorator(func):

        def wrapper(*args, **kwargs):
            # Some aiogram's black magic, need it for availability to put the decorator on handlers
            spec = inspect.getfullargspec(func)
            kwargs = {k: v for k, v in kwargs.items() if k in spec.args}

            asyncio.create_task(handle_event(event))

            if not asyncio.iscoroutinefunction(func):
                async def async_wrapper():
                    return await func(*args, **kwargs)
                return async_wrapper()
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator(_func) if _func else decorator


def manual_track(event: str = None):
    """
    Manual event tracking. Sane as `track` decorator
    :param event:
    :return:
    """
    asyncio.create_task(handle_event(event))
