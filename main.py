from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.database import engine, Base
from app.endpoints import device, user

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения: инициализация БД...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # Передаём управление FastAPI
    await engine.dispose()
    logger.info("Выключение приложения: закрываем соединение...")


app = FastAPI(lifespan=lifespan)

app.include_router(device.router)
app.include_router(user.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
