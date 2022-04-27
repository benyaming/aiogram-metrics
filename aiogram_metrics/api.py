import json
import logging
from datetime import datetime as dt
from typing import Optional

from aiopg import create_pool
from aiogram import Dispatcher
from aiogram.types import Update, User
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from psycopg2.sql import Identifier

from aiogram_metrics.sql import MessageType, init_table, save_event
from aiogram_metrics.hub import Hub


__all__ = [
    'register',
    'close',
    'handle_event'
]


async def _get_user_locale() -> Optional[str]:
    dp = Dispatcher.get_current()
    lang = None

    for middleware in dp.middleware.applications:

        if isinstance(middleware, I18nMiddleware):
            try:
                lang = await middleware.get_user_locale('', (None,))
                break
            except Exception:
                continue

    if not lang:
        user = User.get_current()
        if user.locale:
            lang = user.locale.language

    return lang


async def register(dsn: str, table_name: str):
    Hub.logger = logging.getLogger('aiogram-metrics')

    Hub.logger.debug('Checking database connection...')
    Hub.connection_pool = await create_pool(dsn)

    Hub.logger.debug(f'Checking table {table_name}...')
    Hub.table_name = Identifier(table_name).string
    await init_table()
    Hub.logger.info('Registration complete! Waiting for events...')

    Hub.is_activated = True


async def close():
    if Hub.connection_pool is not None:
        Hub.connection_pool.close()
        Hub.logger.info('Connection pool is now closed. Bue!')


async def handle_event(event: str = None):
    if not Hub.is_activated:
        logging.warning('aiogram-metrics is not registered!')
        return

    update = Update.get_current()
    if update.message:
        user_id = update.message.from_user.id
        message_id = update.message.message_id
        message_data = {'text': update.message.text}
        message_type = (update.message.get_command() and MessageType.command) or MessageType.message
        event = event or update.message.text
    elif update.callback_query:
        user_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id
        message_data = {'callback_data': update.callback_query.data}
        message_type = MessageType.callback
        event = event or update.callback_query.data or update.callback_query.message.text
    else:
        raise ValueError('Unknown message type! Currently supported `message` and `callback_query`.')

    language = await _get_user_locale()
    message_data = json.dumps(message_data, ensure_ascii=False, indent=2)
    event_data = (event, dt.now().isoformat(), user_id, message_id, message_type, message_data, language)
    await save_event(event_data)

    Hub.logger.debug(f'Successfully saved event "{event}"!')
