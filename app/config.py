from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from typing import Optional
import os
from pathlib import Path

load_dotenv()

class Settings(BaseSettings):
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str 
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_NAME: str 
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: str 
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    ALGOLIA_INDEX_NAME:str
    ALGOLIA_APP_ID:str
    ALGOLIA_API_KEY:str
    BASE_DIR: Path = Path(__file__).resolve().parent
    TEMPLATES_DIR: Path = Path(__file__).resolve().parent / "templates"

    model_config = SettingsConfigDict(env_file= ".env")

settings = Settings()

#print (settings.model_dump())
