from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    DB_TYPE: str
    DB_DRIVER: str
    DB_NAME: str
    DB_ECHO: bool
    DATA_PATH: str

    APP_HOST: str
    APP_PORT: int

    LOG_FILE_NAME: str

    TEMP_DIR_PATH: str

    MH_PLATFORM_NAME: str
    MH_BASE_URL: str
    MH_PLATFORM_REGISTRATION_URL: str
    MH_PLATFORM_USER_REGISTRATION_URL: str
    MH_SEND_MESSAGE_URL: str

    THIS_MH_BASE_URL: str

    VK_API_KEY: str
    VK_CALLBACK_KEY: str
    VK_SECRET: str
    VK_API_VERSION: str
    VK_API_COMMUNITY_ID: str
    VK_API_BASE_URL: str

    S3_BUCKET_URL: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_BUCKET_NAME: str

    API_KEY: str | None
    OUT_API_KEY: str | None

    @property
    def FULL_DB_URL(self) -> str:
        return f"{self.DB_TYPE}+{self.DB_DRIVER}:///{self.DATA_PATH}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
