import httpx
from src.settings import settings

import logging

logger = logging.getLogger(__name__)

async def get_user_info(user_id: str)->dict|None:
    try:
        async with httpx.AsyncClient() as client:
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
    
    