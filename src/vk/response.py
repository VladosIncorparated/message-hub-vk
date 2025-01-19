from fastapi import APIRouter, Request, Body, Response, Depends, HTTPException
from src.settings import settings

from src.settings import settings

from src.database.database_engine import get_session, AsyncSession
from src.database.database_schemes import User

import json
import shutil
import os

from sqlalchemy import select, insert

from src.mh_main.request import register_user, send_a_message_to_chat, Message
from src.vk.request import get_user_info

import uuid
from httpx import AsyncClient

from urllib.parse import urlparse

import datetime

router = APIRouter()

async def ansver_confirmation(body: dict, db_session: AsyncSession):
    return Response(content=settings.VK_CALLBACK_KEY, media_type="text/plain")

async def ansver_message_new(body: dict, db_session: AsyncSession):
    object = body["object"]
    message = object["message"]
    vk_user_id = message["from_id"]

    user = (await db_session.execute(select(User).where(User.vk_id==vk_user_id))).scalar_one_or_none()
    if not user:
        user_info = await get_user_info(vk_user_id)

        if user_info:
            user_name = user_info["first_name"]+" "+user_info["last_name"]
            icon_url = user_info["photo_max"]
            
            try:
                temp_dir = f"{settings.TEMP_DIR_PATH}/{str(uuid.uuid4())}"
                os.mkdir(temp_dir, mode=777)

                async with AsyncClient() as client:
                    avatar = await client.get(icon_url)
                    s3_id = uuid.uuid4()
                    avatar_path = temp_dir+f"/{str(s3_id)}.jpg"
                    with open(avatar_path, "wb") as file:
                        file.write(avatar.content)

                    with open(avatar_path) as f:
                        response = await client.put(url=settings.S3_BUCKET_URL+"/"+settings.S3_BUCKET_NAME+"/"+str(s3_id)+".jpg",data=f)
                        response.raise_for_status()
                        icon_url = settings.S3_BUCKET_URL+"/"+settings.S3_BUCKET_NAME+"/"+str(s3_id)+".jpg"
            except Exception as e:
                icon_url=None
            finally:
                shutil.rmtree(temp_dir)

            hm_result = await register_user(settings.MH_BASE_URL+settings.MH_PLATFORM_USER_REGISTRATION_URL, user_name, icon_url)

            await db_session.execute(insert(User).values(
                id = hm_result["user_id"],
                chat_id = hm_result["chat_id"],
                name = user_name,
                vk_id = vk_user_id
            ))

            await db_session.commit()

            user = (await db_session.execute(select(User).where(User.vk_id==vk_user_id))).scalar_one_or_none()
        else:
            raise HTTPException(500)

    if user:
        try:
            temp_dir = f"{settings.TEMP_DIR_PATH}/{str(uuid.uuid4())}"
            os.mkdir(temp_dir, mode=777)

            attachments = {
                "images": [],
                "videos": [],
                "files": [],
            }

            if "attachments" in message:
                for item in message["attachments"]:
                    match(item["type"]):
                        case "photo":
                            url = item["photo"]["orig_photo"]["url"]
                            url_path = urlparse(url).path
                            file_extension = os.path.splitext(url_path)[1]
                            attachments["images"].append(await prepare_file(temp_dir, url, file_extension))
                        case "video":
                            # url = None
                            # async with AsyncClient() as client:
                            #     response = await client.get(
                            #         settings.VK_API_BASE_URL+"/video.get",
                            #         params={
                            #             "videos": f"{item["video"]["owner_id"]}_{item["video"]["id"]}_{item["video"]["access_key"]}",
                            #             # "access_token": settings.VK_API_KEY,
                            #             # "v": settings.VK_API_VERSION,
                            #         },
                            #     )
                            #     url = response

                            # print(url)
                            pass
                        case "doc":
                            name = item["doc"]["title"]
                            file_extension = "."+item["doc"]["ext"]
                            url = item["doc"]["url"]

                            attachments["files"].append(await prepare_file(temp_dir, url, file_extension, name=name))
            
            await send_a_message_to_chat(
                settings.MH_BASE_URL+settings.MH_SEND_MESSAGE_URL,
                Message(
                    id = -1,
                    chat_id=user.chat_id,
                    sender_id=user.id,
                    text=message["text"],
                    sended_at=datetime.datetime.fromtimestamp(message["date"]).isoformat(),
                    attachments=attachments
                )
            )

            return Response(content="ok", media_type="text/plain")
        finally:
            shutil.rmtree(temp_dir)

    

async def prepare_file(temp_dir: str, url_f: str, ext: str, name: str | None = None, url_prew: str | None = None, url_prew_ext: str | None = None) -> dict:
    s3_id = uuid.uuid4()
    temp_name = (name if name else str(s3_id))+ext

    file_url = None

    async with AsyncClient() as client:
        response = await client.get(url_f, follow_redirects=True)
        response = await client.put(url=settings.S3_BUCKET_URL+"/"+settings.S3_BUCKET_NAME+"/"+str(s3_id)+ext,data=response.content)
        response.raise_for_status()
        file_url = settings.S3_BUCKET_URL+"/"+settings.S3_BUCKET_NAME+"/"+str(s3_id)+ext

    if url_prew:
        prew_temp_name = str(uuid.uuid4())+url_prew_ext
        async with AsyncClient() as client:
            response = await client.get(url_prew)
            response = await client.put(url=settings.S3_BUCKET_URL+"/"+settings.S3_BUCKET_NAME+"/"+prew_temp_name,data=response.content)
            response.raise_for_status()
            prew_file_url = settings.S3_BUCKET_URL+"/"+settings.S3_BUCKET_NAME+"/"+prew_temp_name

        return {
            "url": file_url,
            "name":temp_name,
            "miniature":{
                "url": prew_file_url,
            }
        }      
    else:
        return {
            "url": file_url,
            "name": temp_name
        }


call_back_types = {
    "confirmation": ansver_confirmation,
    "message_new": ansver_message_new,
}

@router.post("/vk")
async def call(body: dict = Body(), db_session: AsyncSession = Depends(get_session)):
    if body["secret"] == settings.VK_SECRET:
        return await call_back_types[body["type"]](body, db_session)
    else:
        return ""