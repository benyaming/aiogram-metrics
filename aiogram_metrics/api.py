import json
import logging
from datetime import datetime as dt
from typing import Optional

from aiogram import Dispatcher
from aiogram.types import Update, User, Message, CallbackQuery

try:
    from aiogram.contrib.middlewares.i18n import I18nMiddleware
except ModuleNotFoundError:
    from aiogram.utils.i18n.middleware import I18nMiddleware

from psycopg import AsyncConnection
from psycopg.sql import Identifier

from aiogram_metrics.sql import MessageType, init_table, save_event
from aiogram_metrics.hub import Hub


__all__ = [
    'register',
    'close',
    'handle_event'
]


async def register(dsn: str, table_name: str):
    Hub.logger = logging.getLogger('aiogram-metrics')

    Hub.logger.debug('Checking database connection...')
    Hub.connection = await AsyncConnection.connect(dsn)

    Hub.logger.debug(f'Checking table {table_name}...')
    Hub.table_name = Identifier(table_name).as_string(Hub.connection)
    await init_table()
    Hub.logger.info('Registration complete! Waiting for events...')

    Hub.is_activated = True


async def close():
    if Hub.connection:
        await Hub.connection.close()
        Hub.logger.info('Connection is now closed. Bue!')


async def handle_event(
    event: Optional[str] = None,
    *,
    update: Optional[Update] = None,
    message: Optional[Message] = None,
    callback_query: Optional[CallbackQuery] = None,
    user_id: Optional[int] = None,
):
    if not Hub.is_activated:
        logging.warning('aiogram-metrics is not registered!')
        return

    if not update and not message and not callback_query:
        Hub.logger.info('No update found! Skipping...')

    if (update and update.message) or message:
        message = message or update.message
        user_id = message.chat.id
        message_id = message.message_id
        message_data = {'text': message.text}
        message_type = (message.text.startswith('/') and MessageType.command) or MessageType.message
        event = event or message.text
        language = message.from_user.language_code
    elif (update and update.callback_query) or callback_query:
        callback_query = callback_query or update.callback_query
        user_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
        message_data = {'callback_data': callback_query.data}
        message_type = MessageType.callback
        event = event or callback_query.data or callback_query.message.text
        language = callback_query.from_user.language_code
    elif user_id:
        message_id = language = None
        message_data = {}
        message_type = MessageType.none
    else:
        raise ValueError('Unknown message type! Currently supported `message` and `callback_query`.')

    message_data = json.dumps(message_data, ensure_ascii=False, indent=2)
    event_data = (event, dt.now().isoformat(), user_id, message_id, message_type, message_data, language)
    await save_event(event_data)

    Hub.logger.debug(f'Successfully saved event "{event}"!')
