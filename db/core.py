import asyncpg
from core.env import config
from functools import wraps
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar, AsyncGenerator, Optional
from core.log import logger
from contextlib import asynccontextmanager

_pool: Optional[asyncpg.Pool] = None

async def init_db():
    global _pool
    if _pool is not None:
        return
    
    _pool = await asyncpg.create_pool(
        user=config.DB.USER,
        password=config.DB.PASSWORD,
        database=config.DB.NAME,
        host=config.DB.HOST,
        port=config.DB.PORT,
        min_size=5,
        max_size=20,
        max_queries=50000,
        max_inactive_connection_lifetime=300.0
    )
    logger.info("Database connection pool initialized.")

async def close_db():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed.")

async def get_db_pool() -> asyncpg.Pool:
    if _pool is None:
        await init_db()
    return _pool

# FastAPI Dependency for connections
async def get_db_conn() -> AsyncGenerator[asyncpg.Connection, None]:
    """FastAPI dependency to get a single connection from the pool."""
    pool = await get_db_pool()
    async with pool.acquire() as connection:
        yield connection

@asynccontextmanager
async def atomic() -> AsyncGenerator[asyncpg.Connection, None]:
    """Context manager for transactions."""
    pool = await get_db_pool()
    async with pool.acquire() as connection:
        async with connection.transaction():
            yield connection

P = ParamSpec("P")
R = TypeVar("R")

def with_connection(func: Callable[Concatenate[asyncpg.Connection, P], R]) -> Callable[P, R]:
    """
    Enhanced decorator that uses an existing 'conn' if passed in kwargs,
    otherwise acquires a new one from the pool.
    """
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # If 'conn' is already in kwargs, use it directly (don't acquire new one)
        if 'conn' in kwargs and isinstance(kwargs['conn'], asyncpg.Connection):
            conn = kwargs.pop('conn')
            return await func(conn, *args, **kwargs)
        
        # Otherwise acquire from pool
        pool = await get_db_pool()
        async with pool.acquire() as connection:
            return await func(connection, *args, **kwargs)
    return wrapper

# Legacy support alias
async def get_db():
    return await get_db_pool()
