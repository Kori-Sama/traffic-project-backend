import asyncpg
from core.env import config
from functools import wraps
from typing import Awaitable, Callable, Concatenate, Coroutine, ParamSpec, TypeVar, Any
from core.log import logger

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
    logger.info("Database connection established.")


async def close_db():
    await db.close()
    logger.info("Database connection closed.")


async def get_db():
    return db


P = ParamSpec("P")
R = TypeVar("R")


def with_connection(func: Callable[Concatenate[Any, P], R]) -> Callable[P, R]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        db = await get_db()
        async with db.acquire() as connection:
            return await func(connection, *args, **kwargs)
    return wrapper
