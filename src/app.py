from contextlib import asynccontextmanager

from src.database.create_db import init_models

from fastapi import FastAPI

import os
from .settings import settings

from .logger_conf import init_logger

from src.mh_main.request import register_platform

from src.vk.response import router as vk_router
from src.mh_main.response import router as mh_router

try:
    if not os.path.exists(settings.DATA_PATH):
        os.makedirs(settings.DATA_PATH)
        print("Созданна дериктория данных")
    else:
        print("Дериктория данных существует")
except Exception as e:
    print(f"Ошибка создания директории")
    raise e

try:
    if not os.path.exists(settings.TEMP_DIR_PATH):
        os.makedirs(settings.TEMP_DIR_PATH)
        print("Созданна временная дериктория")
    else:
        print("Временная дериктория существует")
except Exception as e:
    print(f"Ошибка создания временной директории")
    raise e


logger = init_logger()


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

app = FastAPI(lifespan=lifespan)
