from fastapi import APIRouter, Depends, HTTPException
from .schemes import Event, Message
import logging

from src.database.database_engine import get_session,AsyncSession
from src.database.database_schemes import User
from sqlalchemy import select

import uuid
import os
import shutil

router = APIRouter(prefix="/mh")

logger = logging.getLogger(__name__)

async def send_message(event: Event, db_session: AsyncSession ):
    message = Message.model_validate(event.data["message"], from_attributes=True)
    
    users = (await db_session.execute(select(User).where(User.chat_id==message.chat_id))).scalars()

    if not users:
        raise HTTPException(404)

    try:
        temp_dir = f"./temp/{str(uuid.uuid4())}"
        os.mkdir(temp_dir, mode=777)
        media_images = []
        media_video = []
        media_files = []

        if (message.attachments):
            if (message.attachments["images"] and len(message.attachments["images"]) >0):
                for image in messageModel.attachments["images"]:
                    file_path = temp_dir+"/"+str(uuid.uuid4())+"."+image["name"].split(".")[-1]
                    await download_file(image["url"], file_path)
                    media_images.append(types.InputMediaPhoto(media=types.FSInputFile(path=file_path,filename=image["name"])))

            if (messageModel.attachments["videos"] and len(messageModel.attachments["videos"]) >0):
                for video in messageModel.attachments["videos"]:
                    file_path = temp_dir+"/"+str(uuid.uuid4())+"."+video["name"].split(".")[-1]
                    await download_file(video["url"], file_path)
                    media_video.append(types.InputMediaVideo(media=types.FSInputFile(path=file_path, filename=video["name"])))

            if (messageModel.attachments["files"] and len(messageModel.attachments["files"]) >0):
                for file in messageModel.attachments["files"]:
                    file_path = temp_dir+"/"+str(uuid.uuid4())+"."+file["name"].split(".")[-1]
                    await download_file(file["url"], file_path)
                    media_files.append(types.InputMediaDocument(media=types.FSInputFile(path=file_path, filename=file["name"])))

        for user in users:
            try:
                if media_images:
                    await bot.send_media_group(chat_id=user.telegram_id, media=media_images)

                if media_video:
                    await bot.send_media_group(chat_id=user.telegram_id, media=media_video)
                
                if media_files:
                    await bot.send_media_group(chat_id=user.telegram_id, media=media_files)

                if (messageModel.text):
                    await bot.send_message(chat_id=user.telegram_id, text=messageModel.text)
            except Exception as e:
                logger.exception(
                    f"Не удалось отправить сообщение пользователю {user.telegram_id}: {e}",
                    exc_info=False,
                )

    except FailDownload as e:
        logger.exception(
            f"Не удалось скачать файл {e.url}.",
            exc_info=False,
        )
    except Exception as e:
        logger.exception(
            f"Непредвиденная ошибка: {e}",
            exc_info=False,
        )
        raise web.HTTPInternalServerError()
    finally:
        shutil.rmtree(temp_dir)

    return web.Response()


class FailDownload(Exception):
    url: str

    def __init__(self, *args, url: str):
        super().__init__(*args)
        self.url = url

async def download_file(url, save_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(save_path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)  # Чтение файла по 1024 байта
                        if not chunk:
                            break
                        f.write(chunk)
                print(f"Файл успешно сохранен: {save_path}")
            else:
                logger.exception(
                    f"Не удалось скачать файл. Статус: {response.status}",
                    exc_info=False,
                )
                raise FailDownload(url)


event_handlers = {
    "chat.new_message": [
        send_message
    ],
}


@router.post("/webhook/event")
async def event(event: Event, db_session: AsyncSession = Depends(get_session)):
    arr = event_handlers[event.name]
    if arr:
        for item in arr:
            await item(event, db_session)
    else:
        logger.info(f"Ненайден обработчик для события {event.name}.\n", exc_info=False)