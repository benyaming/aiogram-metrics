from psycopg.sql import SQL
from psycopg.errors import DatabaseError

from aiogram_metrics.hub import Hub


class MessageType:
    command = 'command'
    message = 'message'
    callback = 'callback'


async def init_table():
    query = SQL(f'''
        CREATE TABLE IF NOT EXISTS {Hub.table_name} (
        event_type       VARCHAR(256),
        event_date       TIMESTAMP,
        user_id          BIGINT,
        message_id       BIGINT,
        message_type     VARCHAR(256),
        message_data     JSON,
        message_language VARCHAR(32)
        )
    ''')

    try:
        await Hub.connection.execute(query)
        await Hub.connection.commit()
    except DatabaseError:
        Hub.logger.error('Failed to initialize DB tables!')
        await Hub.connection.rollback()

    # async with Hub.connection_pool.acquire() as conn:
    #     async with conn.cursor() as cur:
    #         await cur.execute(query)
    #
    #         if not conn.notices:
    #             Hub.logger.debug(f'Table {Hub.table_name} successfully created!')
    #         else:
    #             Hub.logger.debug(f'Table {Hub.table_name} already exists, skipping...')


async def save_event(event_data: tuple):
    query = SQL(f'INSERT INTO {Hub.table_name} VALUES (%s, %s, %s, %s, %s, %s, %s)')
    await Hub.connection.execute(query, event_data)
    await Hub.connection.commit()
    # async with Hub.connection_pool.acquire() as conn:
    #     async with conn.cursor() as cur:
    #         await cur.execute(query, event_data)
