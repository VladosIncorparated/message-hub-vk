
import logging

import httpx
from httpx import AsyncClient, ConnectError, HTTPStatusError
from pydantic import ValidationError

from fastapi import APIRouter,HTTPException

from src.settings import settings

from .schemes import Message
import uuid

logger = logging.getLogger(__name__)

async def register_platform(mh_url: str, callbak_url: str):
    """
    Регистрация платформы на главном сервере

    :param mh_url: str
    :param url: str
    :return:
    """
    async with AsyncClient() as client:
        try:
            response = await client.post(mh_url,
                                         json={
                                             "platform_name": settings.MH_PLATFORM_NAME,
                                             "url": callbak_url
                                         })
            logger.info(response.text)
        except httpx.ReadTimeout:
            raise Exception("Главный сервер не в сети. Время ожидания ответа превышено")
        except ConnectError:
            raise Exception("Главный сервер не в сети")
        if response.status_code == 404:
            raise Exception("Неверный url главного сервера")
        elif response.status_code == 422:
            raise Exception("Неверный запрос на регистрацию платформы")


async def register_user(mh_url, name: str, icon_url: str | None, platform_name: str = settings.MH_PLATFORM_NAME) -> dict:
    async with AsyncClient() as client:
        try:
            response = await client.post(mh_url,
                                         json={
                                             "platform_name": platform_name, 
                                             "name": name,
                                             "icon_url": icon_url,
                                             })
            response.raise_for_status()
            return response.json()
        except HTTPException as e:
            logger.error(f"Error:{e}")
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail="Ошибка регистрации пользователя на основном сервере")


async def send_a_message_to_chat(mh_url: str, message: Message):
    """
    Отправляет сообщение на главный сервер

    :param message: Message
    :return: None
    """
    async with AsyncClient() as client:
        try:
            response = await client.post(
                url=mh_url,
                json={
                    "message": message.model_dump(),
                    "event_id":str(uuid.uuid4()),
                },
                timeout=3000
            )
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as e:
            print(f"http Error: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e
