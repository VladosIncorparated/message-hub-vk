from fastapi import APIRouter, Depends, HTTPException
from .schemes import Event, Message
import logging

from src.database.database_engine import get_session,AsyncSession
from src.database.database_schemes import User
from sqlalchemy import select

from src.vk.request import phots_get_messages_upload_server, upload_photo, save_messages_photo, message_send

import httpx

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

        attachments = []

        if (message.attachments):
            if (message.attachments["images"] and len(message.attachments["images"]) >0):
                upload_url = (await phots_get_messages_upload_server())["upload_url"]

                for image in message.attachments["images"]:
                    file_path = temp_dir+"/"+str(uuid.uuid4())+"."+image["name"].split(".")[-1]

                    await download_file(image["url"], file_path)

                    upload_photo_info = await upload_photo(upload_url, file_path)

                    save_photo_info = (await save_messages_photo(upload_photo_info["server"], upload_photo_info["photo"], upload_photo_info["hash"]))[0]

                    attachments.append(f"photo{str(save_photo_info["owner_id"])}_{str(save_photo_info["id"])}")

            # if (messageModel.attachments["videos"] and len(messageModel.attachments["videos"]) >0):
            #     for video in messageModel.attachments["videos"]:
            #         file_path = temp_dir+"/"+str(uuid.uuid4())+"."+video["name"].split(".")[-1]
            #         await download_file(video["url"], file_path)
            #         media_video.append(types.InputMediaVideo(media=types.FSInputFile(path=file_path, filename=video["name"])))

            # if (messageModel.attachments["files"] and len(messageModel.attachments["files"]) >0):
            #     for file in messageModel.attachments["files"]:
            #         file_path = temp_dir+"/"+str(uuid.uuid4())+"."+file["name"].split(".")[-1]
            #         await download_file(file["url"], file_path)
            #         media_files.append(types.InputMediaDocument(media=types.FSInputFile(path=file_path, filename=file["name"])))
        
        chunced_attachments = [",".join(attachments[i:i + 10]) for i in range(0, len(attachments), 10)]

        for user in users:
            try:
                for chunc in chunced_attachments:
                    await message_send(user.vk_id, None, chunc)

                await message_send(user.vk_id, message.text, None)

            except Exception as e:
                logger.exception(
                    f"Не удалось отправить сообщение пользователю {user.vk_id}: {e}",
                    exc_info=False,
                )
    except Exception as e:
        logger.exception(
            f"Непредвиденная ошибка: {e}",
            exc_info=False,
        )
        raise HTTPException(500)
    finally:
        shutil.rmtree(temp_dir)


async def download_file(url, save_path):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            f.write(response.content)


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