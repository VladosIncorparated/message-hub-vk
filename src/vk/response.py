from fastapi import APIRouter, Request, Body, Response, Depends, HTTPException
from src.settings import settings

from src.settings import settings

from src.database.database_engine import get_session, AsyncSession
from src.database.database_schemes import User

import json
import shutil
import os

from sqlalchemy import select, insert

from src.mh_main.request import register_user
from src.vk.request import get_user_info

import uuid
from httpx import AsyncClient

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

            user = (await db_session.execute(select(User).where(User.vk_id==vk_user_id))).scalar_one_or_none()
        else:
            raise HTTPException(500)

    if user:
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
        pass

    

async def prepare_file(temp_dir: str, bot_file_id, file_pref: str = None, file_name: str = None, video: bool = None) -> dict:
    file = await bot.get_file(bot_file_id)
    
    s3_id = uuid.uuid4()

    local_file_path = temp_dir+"/"+str(s3_id)+(file_pref if file_pref else "."+file_name.split(".")[-1])

    await bot.download_file(file.file_path, local_file_path)

    url = None

    with open(local_file_path, "rb") as f:
        async with aiohttp.ClientSession() as session:
            async with session.put(url=S3_BUCKET_URL+"/"+str(s3_id)+(file_pref if file_pref else "."+file_name.split(".")[-1]),data=f) as response:
                url = S3_BUCKET_URL+"/"+str(s3_id)+(file_pref if file_pref else "."+file_name.split(".")[-1])
                response.raise_for_status()


    if video:
        return {
            "url": url,
            "name": str(s3_id)+file_pref if file_pref else file_name,
            "miniature":{
                "url": await generete_prevue(temp_dir, local_file_path)
            }
        }      
    else:
        return {
            "url": url,
            "name": str(s3_id)+file_pref if file_pref else file_name
        }

async def generete_prevue(temp_dir: str,video_name: str):
    clip = VideoFileClip(video_name)
    frame = clip.get_frame(2)
    image = Image.fromarray(frame)
    
    output_filename = str(uuid.uuid4())+".jpg"

    image.save(temp_dir+'/'+output_filename)

    clip.close()
    image.close()

    with open(temp_dir+'/'+output_filename, "rb") as f:
        async with aiohttp.ClientSession() as session:
            async with session.put(url=S3_BUCKET_URL+"/"+output_filename,data=f) as response:
                response.raise_for_status()
                return S3_BUCKET_URL+"/"+output_filename


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