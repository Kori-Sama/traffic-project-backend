from os import getenv
from dotenv import load_dotenv


load_dotenv(override=True)


class Config:
    PORT: int = int(getenv('PORT', '8000'))

    class _DB:
        HOST: str = getenv('DB_HOST', 'localhost')
        PORT: str = getenv('DB_PORT', '5432')
        USER: str = getenv('DB_USER', 'postgres')
        PASSWORD: str = getenv('DB_PASSWORD', '')
        NAME: str = getenv('DB_NAME', 'traffic')

    DB: _DB = _DB()


config = Config()