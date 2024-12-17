import asyncpg
from core.env import config
from functools import wraps
from typing import Callable, Any

db = None


async def init_db():
    global db
    db = await asyncpg.create_pool(
        user=config.DB.USER,
        password=config.DB.PASSWORD,
        database=config.DB.NAME,
        host=config.DB.HOST,
        port=config.DB.PORT
    )
    print("Database initialized.")


async def close_db():
    await db.close()
    print("Database connection closed.")


async def get_db():
    return db


def with_connection(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        db = await get_db()
        async with db.acquire() as connection:
            return await func(connection, *args, **kwargs)
    return wrapper
