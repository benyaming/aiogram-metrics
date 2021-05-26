from aiopg import Connection, Cursor
from psycopg2.sql import SQL, Identifier

from hub import Hub


async def init_table(table_name: str):
    init_query = SQL(f'''
    create table if not exists {Identifier(table_name).string} (
    event_type       varchar(256),
    event_date       timestamp,
    user_id          bigint,
    message_id       bigint,
    message_type     varchar(256),
    message_data     json,
    message_language varchar(32)
)''')
    conn: Connection
    cur: Cursor

    async with Hub.connection_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(init_query)
