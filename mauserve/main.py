"""Главный файл сервера.

Производит полную настройку и подключение всех компонентов.
В том числе настраивает подключение базы данных и всех обработчиков.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Подгружаем роутеры
from tortoise import generate_config
from tortoise.contrib.fastapi import RegisterTortoise

from mauserve.config import config
from mauserve.leaderbord.router import router as leaderbord_router
from mauserve.roomlist.router import router as rooms_router
from mauserve.users.router import router as user_router

# Жизненный цикл базы данных
# ==========================

DB_CONFIG = generate_config(
    config.test_db_url if config.debug else config.db_url,
    app_modules={"models": ["mauserve.models", "aerich.models"]},
    testing=config.debug,
    connection_label="models",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Жизненный цикл базы данных.

    Если это тестовая сессия, то создаёт базу данных в оперативной
    памяти.
    Иначе же просто  к базе данных postgres, на всё время
    работы сервера.
    """
    async with RegisterTortoise(
        app=app,
        config=DB_CONFIG,
        generate_schemas=True,
        add_exception_handlers=True,
    ):
        # db connected
        yield
        # app teardown

    # db connections closed
    # ? Тут мог бы быть более корректный код, но увы
    # if config.debug:
    #     await Tortoise._drop_databases()


# Константы
# =========

app = FastAPI(
    lifespan=lifespan,
    title="mauserve",
    debug=config.debug,
    version="v0.3.2",
    root_path="/api",
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключает сторонние роутеры
app.include_router(user_router)
app.include_router(leaderbord_router)
app.include_router(rooms_router)
