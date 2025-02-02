from contextlib import asynccontextmanager

from src.database.create_db import init_models

from fastapi import FastAPI

import os
from .settings import settings

from .logger import logger

from src.mh_main.request import register_platform

from src.vk.response import router as vk_router
from src.mh_main.response import router as mh_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.include_router(vk_router)
    app.include_router(mh_router)
    # app.include_router(webhooks_router, tags=["webhook"])

    try:
        if not os.path.exists(settings.DATA_PATH+"/"+settings.DB_NAME):
            await init_models()
            logger.debug("База данных готова")
        else:
            logger.debug("База данных существует")
    except Exception as e:
        logger.error(f"Ошибка создания базы данных")
        raise e

    try:
        await register_platform(settings.MH_BASE_URL+settings.MH_PLATFORM_REGISTRATION_URL, settings.THIS_MH_BASE_URL)
        logger.debug("Регистрация платформы прошла успешно")
    except Exception as e:
        logger.error(f"Ошибка регистрации платформы")
        raise e
    logger.debug("Приложение успешно запущено")
    yield
    logger.debug("Приложение успешно остановлено")

if settings.API_KEY:
    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
else:
    app = FastAPI(lifespan=lifespan)