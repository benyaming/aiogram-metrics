from logging import Logger

from psycopg import AsyncConnection


class Hub:
    is_activated: bool = False
    connection: AsyncConnection = None
    table_name: str = None
    logger: Logger
