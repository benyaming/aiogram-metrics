import datetime

from aiogram.types import User, Message, Update
from aiopg import Connection, Cursor
from psycopg2.sql import SQL, Identifier
from psycopg2.extras import Json

import aiogram_metrics.hub as hub


class MessageType:
    command = 'command'
    message = 'message'
    callback = 'callback'


async def init_table():
    query = SQL(f'''
    create table if not exists {hub.Hub.table_name} (
    event_type       varchar(256),
    event_date       timestamp,
    user_id          bigint,
    message_id       bigint,
    message_type     varchar(256),
    message_data     json,
    message_language varchar(32)
)''')

    async with hub.Hub.connection_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query)


async def save_event(event_data: tuple):
    query = SQL(f'INSERT INTO {hub.Hub.table_name} VALUES (%s, %s, %s, %s, %s, %s, %s)')

    async with hub.Hub.connection_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, event_data)
