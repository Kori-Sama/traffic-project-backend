from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core import env
from core.middleware import middlewares
from db.core import close_db, init_db
from core.utils import load_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan, middleware=middlewares)

app.mount("/videos", StaticFiles(directory="videos"), name="video")


load_routers(app, "router")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, port=env.config.PORT)
