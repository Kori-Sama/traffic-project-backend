import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


async def main():
    from db.core import get_db, init_db, close_db
    await init_db()
    with open("sql/init.sql", 'r') as f:
        sql = f.read()
        # print(sql)
        db = await get_db()
        await db.execute(sql)
    await close_db()

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
