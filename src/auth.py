from fastapi import FastAPI, Depends, Request, HTTPException
from src.settings import settings
from src.logger import logger
import datetime

async def verify_api_key(request: Request):
    if settings.API_KEY:
        key = request.headers.get("API-KEY")
        if key:
            if key == settings.API_KEY:
                return key
            else:
                logger.info(f"Нверный API_KEY {key}.")
                raise HTTPException(422)
        else:
            raise HTTPException(422)
    else:
        return "Test mode"