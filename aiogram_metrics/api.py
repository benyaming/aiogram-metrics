from aiopg import create_pool

from aiogram_metrics.sql import init_table
from hub import Hub


async def register(dsn: str, table_name: str, ):
    Hub.connection_pool = await create_pool(dsn)
    await init_table(table_name)

    Hub.is_activated = True
