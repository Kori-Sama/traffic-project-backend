from tortoise import Tortoise

from core import env


async def init_orm():
    await Tortoise.init(config={
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "host": env.config.DB.HOST,
                    "port": env.config.DB.PORT,
                    "user": env.config.DB.USER,
                    "password": env.config.DB.PASSWORD,
                    "database": env.config.DB.NAME,
                    "max_size": 10,
                    "ssl": False
                }
            }
        },
        "apps": {
            "models": {
                "models": ["models"],
                "default_connection": "default"
            }
        }})
    await Tortoise.generate_schemas()


async def close_orm():
    await Tortoise.close_connections()
