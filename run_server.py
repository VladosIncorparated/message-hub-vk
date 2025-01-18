import uvicorn
from src.app import app
from src.settings import settings

uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
