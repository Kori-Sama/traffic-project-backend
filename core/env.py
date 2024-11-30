from os import getenv
from dotenv import load_dotenv
import os


load_dotenv()


class Config:
    PORT: int = int(getenv('PORT'))

    class _DB:
        HOST: str = getenv('DB_HOST')
        PORT: str = getenv('DB_PORT')
        USER: str = getenv('DB_USER')
        PASSWORD: str = getenv('DB_PASSWORD')
        NAME: str = getenv('DB_NAME')

    DB: _DB = _DB()


config = Config()
