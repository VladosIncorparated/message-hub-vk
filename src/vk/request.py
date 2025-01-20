from httpx import AsyncClient
from src.settings import settings

import logging

import random

logger = logging.getLogger(__name__)

async def get_user_info(user_id: str)->dict|None:
    try:
        async with AsyncClient() as client:
            response = await client.get(
                settings.VK_API_BASE_URL+"/users.get",
                params={
                    "user_ids": user_id,
                    "fields": "photo_max",
                    "access_token": settings.VK_API_KEY,
                    "v": settings.VK_API_VERSION,
                },
            )
        
        response.raise_for_status()
        # Парсим JSON-ответ
        response_data = response.json()
        
        # Проверяем, есть ли в ответе данные
        if "response" in response_data:
            user_info = response_data["response"][0]
            return user_info
        else:
            return None

    except Exception as e:
        return None
    

async def phots_get_messages_upload_server()->dict:
    """
    return: {
        "album_id":-64,
        "upload_url":"https:\/\/pu.vk.com\/c231331\/ss2269\/upload.php?act=do_add&mid=743784474&aid=-64&gid=218252175&hash=2e60ee02a7dd5aaaf0bce3e034b1dc30&rhash=eda561bac91afb0270fc9ca741ac626b&swfupload=1&api=1&mailphoto=1",
        "user_id":0,
        "group_id":218252175
    }
    """
    async with AsyncClient() as client:
        response = await client.get(
            settings.VK_API_BASE_URL+"/photos.getMessagesUploadServer",
            params={
                "group_id": settings.VK_API_COMMUNITY_ID,
                "access_token": settings.VK_API_KEY,
                "v": settings.VK_API_VERSION,
            },
        )
    
    response.raise_for_status()
    response_data = response.json()
    
    # Проверяем, есть ли в ответе данные
    if "response" in response_data:
        url_info = response_data["response"]
        return url_info
    else:
        raise Exception("phots_get_messages_upload_server not data")


async def upload_photo(url: str, file_path: str)->dict:
    """
    return: {
        "server":231331,
        "photo":"[{\"markers_restarted\":true,\"photo\":\"f7cdd492d6:w\",\"sizes\":[],\"latitude\":0,\"longitude\":0,\"kid\":\"63339bce9aa7110b118709d208f4f605\",\"sizes2\":[[\"s\",\"2169b25ce7ab50db8883a22c2f01f10e3b14030beca59a61e5184e40\",\"-8077041814521722093\",75,50],[\"m\",\"532f75fa48381e7c22ac2208fd0dc09585fca2e7c7af8fe73e51ad10\",\"2481357305209911761\",130,87],[\"x\",\"04ec4c4702bcaed3a751c1be7cecdfac77707c1fb6baba086f75ba69\",\"7060873775304692609\",604,402],[\"y\",\"735b15dc188c8d9f7665e63d10d65f709d5c2c5fcc7c1cf4235887dc\",\"-247552755041223595\",807,537],[\"z\",\"69dd5cf636aed29fb13f019924fe256e4ea61465304f6a58ad687d2b\",\"-5038604692102399322\",1280,852],[\"w\",\"8772eaa43776efbc784d0ffa0459eb78f498958302859a574c815b7e\",\"22189486849580549\",2560,1704],[\"o\",\"532f75fa48381e7c22ac2208fd0dc09585fca2e7c7af8fe73e51ad10\",\"2481357305209911761\",130,87],[\"p\",\"b272a37f1d0e68a1041b1e530f021de86de255f0668c086fe8207c75\",\"-3609630020141000359\",200,133],[\"q\",\"61208ee4d94149963f6d7db4e0ae2e3a6bdde6fef60e5a81c7e76081\",\"-4859686797456740524\",320,213],[\"r\",\"e0a963afe97cb480055bdce5cfcb756c15a0e86af7b461eba0db05d0\",\"4955764010854965486\",510,340]],\"urls\":[],\"urls2\":[\"IWmyXOerUNuIg6IsLwHxDjsUAwvspZph5RhOQA/E8t0gUOV6I8.jpg\",\"Uy91-kg4HnwirCII_Q3AlYX8oufHr4_nPlGtEA/0XnbgVKNbyI.jpg\",\"BOxMRwK8rtOnUcG-fOzfrHdwfB-2uroIb3W6aQ/gVPo3ElD_WE.jpg\",\"c1sV3BiMjZ92ZeY9ENZfcJ1cLF_MfBz0I1iH3A/VTyZtBSEkPw.jpg\",\"ad1c9jau0p-xPwGZJP4lbk6mFGUwT2pYrWh9Kw/prqea7pHE7o.jpg\",\"h3LqpDd277x4TQ_6BFnrePSYlYMChZpXTIFbfg/Bd5qgTjVTgA.jpg\",\"Uy91-kg4HnwirCII_Q3AlYX8oufHr4_nPlGtEA/0XnbgVKNbyI.jpg\",\"snKjfx0OaKEEGx5TDwId6G3iVfBmjAhv6CB8dQ/WdnoDp8E6M0.jpg\",\"YSCO5NlBSZY_bX204K4uOmvd5v72DlqBx-dggQ/VG_v_Zrsjrw.jpg\",\"4Kljr-l8tIAFW9zlz8t1bBWg6Gr3tGHroNsF0A/7uCscRxpxkQ.jpg\"]}]",
        "hash":"4dc524efee95578c69883f897087bd77"
    }
    """
    with open(file_path, 'rb') as photo_file:
        files = {"file": ('image.jpg', photo_file, 'image/jpeg')}
        async with AsyncClient() as client:
            response = await client.post(
                url,
                files=files,
                # data=photo_file.read(),
            )
    
            response.raise_for_status()
            response_data = response.json()
            
            return response_data
        

async def save_messages_photo(server: str, photo: dict, hash: str)->dict:
    """
    return:[
            {
                "album_id":-64,
                "date":1673862629,
                "id":457239023,
                "owner_id":-218252175,
                "access_key":"698e738862a7917b5b",
                "sizes":[
                    {
                    "height":50,
                    "type":"s",
                    "width":75,
                    "url":"https:\/\/sun9-west.userapi.com\/sun9-45\/s\/v1\/ig2\/Vus7E6r8jZjgv5E9bnuM6fbvL9U_NP4-goegNOaEy8t4Z1DnzofjER9exwblecB6Hxb3EUbWv7lQvxdRaErZGoT3.jpg?size=75x50&quality=96&type=album"
                    },
                    {
                    "height":87,
                    "type":"m",
                    "width":130,
                    "url":"https:\/\/sun9-west.userapi.com\/sun9-45\/s\/v1\/ig2\/JTtJ-M4Y1Md4nbNyY6QNKBjs9xleCGkDwGw-NuMvLV0DKfQrPb_xN7QcfazSTrBcZ-_JzsJ21pTuLI7Slr8m9HcB.jpg?size=130x87&quality=96&type=album"
                    },
                    {
                    "height":402,
                    "type":"x",
                    "width":604,
                    "url":"https:\/\/sun9-west.userapi.com\/sun9-45\/s\/v1\/ig2\/2DBzUBeOMpydPcypQFkirgj6g9mzsj8le0qsrWQ_lPX3zNQN1229bLivxf26ya-91HF9D57exLSnkSnJwUxJdUBN.jpg?size=604x402&quality=96&type=album"
                    },
                    {
                    "height":537,
                    "type":"y",
                    "width":807,
                    "url":"https:\/\/sun9-west.userapi.com\/sun9-45\/s\/v1\/ig2\/Biye5eNVG4UA_ymuN60MU6Qp26yO7rYp0WB-ch55oxkaATpXs4Kmqqznz1keCYHg_BHyvPhyrSGyK3zRK29LoVKH.jpg?size=807x537&quality=96&type=album"
                    },
                    {
                    "height":852,
                    "type":"z",
                    "width":1280,
                    "url":"https:\/\/sun9-west.userapi.com\/sun9-45\/s\/v1\/ig2\/O-BkqGyWMw2ZKcOyYz8sH543Ihkws7mAn6x76JYh0mVW2MCR9x9eig_AS6gT6OLeySlvewx5oyri1Ejj0uNhJuKo.jpg?size=1280x852&quality=96&type=album"
                    },
                    {
                    "height":1704,
                    "type":"w",
                    "width":2560,
                    "url":"https:\/\/sun9-west.userapi.com\/sun9-45\/s\/v1\/ig2\/o5klH0kpqicWBkDGQl_ch2j8VRpW69xrnq_PXw823wrMYc2qnXQLuDZeECtcKSaka1gfCpP9smoz7XwGAMDTk7vo.jpg?size=2560x1704&quality=96&type=album"
                    },
                    {
                    "height":87,
                    "type":"o",
                    "width":130,
                    "url":"https:\/\/sun9-west.userapi.com\/sun9-45\/s\/v1\/ig2\/JTtJ-M4Y1Md4nbNyY6QNKBjs9xleCGkDwGw-NuMvLV0DKfQrPb_xN7QcfazSTrBcZ-_JzsJ21pTuLI7Slr8m9HcB.jpg?size=130x87&quality=96&type=album"
                    },
                    {
                    "height":133,
                    "type":"p",
                    "width":200,
                    "url":"https:\/\/sun9-west.userapi.com\/sun9-45\/s\/v1\/ig2\/dFvcZ_sYZeMJtmvotINsevf_0x4KbDxo-jcrZojRQtebIKvM0juMU9U9NjybaidOukkrImr2CWcW8u6IHdlceWKD.jpg?size=200x133&quality=96&type=album"
                    },
                    {
                    "height":213,
                    "type":"q",
                    "width":320,
                    "url":"https:\/\/sun9-west.userapi.com\/sun9-45\/s\/v1\/ig2\/GglL_Kv0x1_rnPwXwtTPZUMFg9sT_JB9xUSUeNvNIRapPRhGvQbQAaCwD57WBhUKU8sPD6-BhyadPIXaALqERkS1.jpg?size=320x213&quality=96&type=album"
                    },
                    {
                    "height":340,
                    "type":"r",
                    "width":510,
                    "url":"https:\/\/sun9-west.userapi.com\/sun9-45\/s\/v1\/ig2\/LnQwirb-SUb689R2k90Q8MwuwHJ0tfO03a0IkCeXObaQERRE2-UUyLBCTTLme2qkLcxXAekHVbkLMEZhRq5E6Ggr.jpg?size=510x340&quality=96&crop=2,0,2556,1704&type=album"
                    }
                ],
                "text":"",
                "user_id":100,
                "has_tags":false
            }
        ]
    """
    async with AsyncClient() as client:
        response = await client.post(
            settings.VK_API_BASE_URL+"/photos.saveMessagesPhoto",
            data={
                "photo": photo,
                "hash": hash,
                "server": server,
                "access_token": settings.VK_API_KEY,
                "v": settings.VK_API_VERSION,
            },
        )

        response.raise_for_status()
        response_data = response.json()
        
        if "response" in response_data:
            return response_data["response"]
        else:
            raise Exception("phots_get_messages_upload_server not data")
        

async def message_send(user_id: str, text: str | None, attachment: str | None, reply_to: str | None = None):
    """
    Отправка сообщения

    """
    async with AsyncClient() as client:
        data={
            "user_id":user_id,
            "random_id": random.randint(1, 2147483647),
            "access_token": settings.VK_API_KEY,
            "v": settings.VK_API_VERSION,
        }
        if text:
            data["message"]=text
        if attachment:
            data["attachment"] = attachment
        if reply_to:
            data["reply_to"]=reply_to
        response = await client.post(
            settings.VK_API_BASE_URL+"/messages.send",
            data=data,
        )

        response.raise_for_status()
        return response.json()
        

async def docs_get_messages_upload_server(peer_id)->dict:
    """
    return: {
        "upload_url":"https:\/\/pu.vk.com\/c240331\/upload_doc.php?act=add_doc&mid=743784474&aid=0&gid=0&type=0&hash=ae6f11219f2e21f9ad7825b1739141b3&rhash=69c202cbb175d33099a56d8aaf42f369&api=1"
    }
    """
    async with AsyncClient() as client:
        response = await client.get(
            settings.VK_API_BASE_URL+"/docs.getMessagesUploadServer",
            params={
                "peer_id": peer_id,
                "access_token": settings.VK_API_KEY,
                "v": settings.VK_API_VERSION,
            },
        )
    
    response.raise_for_status()
    response_data = response.json()
    
    # Проверяем, есть ли в ответе данные
    if "response" in response_data:
        url_info = response_data["response"]
        return url_info
    else:
        raise Exception("docs_get_messages_upload_server not data")



async def upload_doc(url: str, file_name, file_path: str)->dict:
    """
    return: {
        "file":"743784474|0|0|240331|e24cd4aa3c|pdf|14854|\u041f\u0435\u0440\u0432\u044b\u0435 \u0448\u0430\u0433\u0438.pdf|00a3fc6e249ee1196593627b888e2187|8775d2ed941fb21e014f14ede3d61a9c||||eyJkaXNrIjozfQ=="
    }
    """
    with open(file_path, 'rb') as doc_file:
        files = {"file": (file_name, doc_file)}
        async with AsyncClient() as client:
            response = await client.post(
                url,
                files=files,
            )
    
            response.raise_for_status()
            response_data = response.json()
            
            return response_data


async def save_docs(file: dict)->dict:
    """
    return:{
        "type":"doc",
        "doc":{
        "id":657626222,
        "owner_id":743784474,
        "title":"\\u041f\\u0435\\u0440\\u0432\\u044b\\u0435 \\u0448\\u0430\\u0433\\u0438.pdf",
        "size":14854,
        "ext":"pdf",
        "date":1674050872,"type":1,
        "url":"https:\/\/vk.com\/doc743784474_657626222?hash=jWHXvoUCYCxklaOiBsI0bZRACXzH6CiauvHlkgrIjYg&dl=G42DGNZYGQ2DONA:1674050872:7rxkHS8nSaTa5C0DkRfjpZZagKIs1Z3lKnPABTOqr4P&api=1&no_preview=1"
        }
    }
    """
    async with AsyncClient() as client:
        response = await client.post(
            settings.VK_API_BASE_URL+"/docs.save",
            data={
                "file": file,
                "access_token": settings.VK_API_KEY,
                "v": settings.VK_API_VERSION,
            },
        )

        response.raise_for_status()
        response_data = response.json()
        
        if "response" in response_data:
            return response_data["response"]
        else:
            raise Exception("phots_get_messages_upload_server not data")
