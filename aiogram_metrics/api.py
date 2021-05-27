import json
from datetime import datetime as dt
from json import dumps

from aiopg import create_pool
from aiogram.types import Update
from psycopg2.sql import Identifier
from psycopg2.extras import Json

from aiogram_metrics.sql import MessageType, init_table, save_event
import aiogram_metrics.hub as hub


async def register(dsn: str, table_name: str, ):
    hub.Hub.connection_pool = await create_pool(dsn)
    hub.Hub.table_name = Identifier(table_name).string
    await init_table()

    hub.Hub.is_activated = True


async def close():
    if hub.Hub.connection_pool is not None:
        await hub.Hub.connection_pool.close()


async def track(event: str):
    update = Update.get_current()
    if update.message:
        user_id = update.message.from_user.id
        message_id = update.message.message_id
        message_data = {'text': update.message.text}
        message_type = (update.message.get_command() and MessageType.command) or MessageType.message
    elif update.callback_query:
        user_id = update.callback_query.message.from_user.id
        message_id = update.callback_query.message.message_id
        message_data = {'callback_data': update.callback_query.data}
        message_type = MessageType.callback
    else:
        raise ValueError('Unknown message type! Currently supported `message` and `callback_query`.')

    message_data = json.dumps(message_data, ensure_ascii=False, indent=2)
    event_data = (event, dt.now().isoformat(), user_id, message_id, message_type, message_data, None)  # todo lang
    await save_event(event_data)


