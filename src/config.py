from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    BOT_TOKEN: str

    DB_HOST: str 
    DB_PORT: int 
    DB_USER: str 
    DB_PASS: str
    DB_NAME: str 

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
