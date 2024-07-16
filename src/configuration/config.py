from typing import List
from pydantic import  ValidationError, validator, EmailStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USER: str
    REDIS_PASSWORD: str
    REDIS_QUEUE: str

    LOG_FILE: str

    LOGO_FILEPATH: str

    IDVENDOR: int
    IDPRODUCT: int
    IN_EP: int
    OUT_EP: int


    # idVendor=0x03F0, idProduct=0x0E69, in_ep=0x82, out_ep=0x02

    # AWS_ACCESS_KEY_ID: str
    # AWS_SECRET_ACCESS_KEY: str
    # AWS_REGION: str

    # EMAIL_FROM: EmailStr
    # EMAIL_TO: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

try:
    settings = Settings()
except ValidationError as e:
    print("Validation error:", e)
    exit()
