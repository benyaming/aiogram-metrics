from aiopg import Pool


class Hub:
    is_activated: bool = False
    connection_pool: Pool = None
    table_name: str = None
