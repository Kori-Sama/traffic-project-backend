from fastapi import FastAPI

from core import env
from core.middleware import middlewares
from core.db import close_orm, init_orm
from core.utils import load_routers

app = FastAPI(
    on_startup=[init_orm],
    on_shutdown=[close_orm],
    middleware=middlewares
)


load_routers(app, "router")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, port=env.config.PORT)
