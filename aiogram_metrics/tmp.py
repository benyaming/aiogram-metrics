import asyncio
import api


dsn = 'host=localhost dbname=aiogram_metrics user=postgres password=qrx59Opri'


async def main():
    await api.register(dsn, 'test',)


asyncio.run(main())


# todo: ResourceWarning: Unclosed 1 connections in <aiopg.pool.Pool object at 0x0315DDF0>
