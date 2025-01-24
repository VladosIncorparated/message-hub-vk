from fastapi import APIRouter, Depends, HTTPException
from .schemes import Event, Message
import logging

from src.database.database_engine import get_session,AsyncSession
from src.database.database_schemes import User
from sqlalchemy import select

from src.vk.request import phots_get_messages_upload_server, upload_photo, save_messages_photo, message_send, docs_get_messages_upload_server, upload_doc, save_docs

import httpx

import uuid
import os
import shutil

router = APIRouter(prefix="/mh")

logger = logging.getLogger(__name__)

async def send_message(event: Event, db_session: AsyncSession ):
    message = Message.model_validate(event.data["message"], from_attributes=True)
    
    users = (await db_session.execute(select(User).where(User.chat_id==message.chat_id, User.id!=message.sender_id))).scalars()

    if not users:
        raise HTTPException(404)

    try:
        temp_dir = f"./temp/{str(uuid.uuid4())}"
        os.mkdir(temp_dir, mode=777)

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


        for user in users:
            file_attachments = []

            if (message.attachments["files"] and len(message.attachments["files"]) >0):
                upload_url = (await docs_get_messages_upload_server(user.vk_id))["upload_url"] # Для конкретного пользователя, мож как-то подругому, но для сообщества не работает

                for file in message.attachments["files"]:
                    file_path = temp_dir+"/"+str(uuid.uuid4())+"."+file["name"].split(".")[-1]
                    await download_file(file["url"], file_path)

                    upload_doc_info = await upload_doc(upload_url, file["name"], file_path)

                    save_doc_info = await save_docs(upload_doc_info["file"])

                    file_attachments.append(f"doc{str(save_doc_info["doc"]["owner_id"])}_{str(save_doc_info["doc"]["id"])}")


            if (message.attachments["videos"] and len(message.attachments["videos"]) >0):
                upload_url = (await docs_get_messages_upload_server(user.vk_id))["upload_url"] # Для конкретного пользователя, мож как-то подругому, но для сообщества не работает

                for file in message.attachments["videos"]:
                    file_path = temp_dir+"/"+str(uuid.uuid4())+"."+file["name"].split(".")[-1]
                    await download_file(file["url"], file_path)

                    upload_doc_info = await upload_doc(upload_url, file["name"], file_path)

                    save_doc_info = await save_docs(upload_doc_info["file"])

                    file_attachments.append(f"doc{str(save_doc_info["doc"]["owner_id"])}_{str(save_doc_info["doc"]["id"])}")

            sum_attachments = attachments+file_attachments
            chunced_attachments = [",".join(sum_attachments[i:i + 10]) for i in range(0, len(sum_attachments), 10)]

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
    if event.name in event_handlers:
        arr = event_handlers[event.name]
        if arr:
            for item in arr:
                await item(event, db_session)
    else:
        logger.info(f"Ненайден обработчик для события {event.name}.\n", exc_info=False)