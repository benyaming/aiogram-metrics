from psycopg2.sql import SQL

from aiogram_metrics.hub import Hub


class MessageType:
    command = 'command'
    message = 'message'
    callback = 'callback'


async def init_table():
    query = SQL(f'''
    create table if not exists {Hub.table_name} (
    event_type       varchar(256),
    event_date       timestamp,
    user_id          bigint,
    message_id       bigint,
    message_type     varchar(256),
    message_data     json,
    message_language varchar(32)
)''')

    async with Hub.connection_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query)

            if not conn.notices:
                Hub.logger.debug(f'Table {Hub.table_name} successfully created!')
            else:
                Hub.logger.debug(f'Table {Hub.table_name} already exists, skipping...')


async def save_event(event_data: tuple):
    query = SQL(f'INSERT INTO {Hub.table_name} VALUES (%s, %s, %s, %s, %s, %s, %s)')

    async with Hub.connection_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, event_data)
