from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url:str
    app_name:str
    app_env:str
    app_version:str
    secret_key:str
    algorithm:str
    access_token_expire_minutes:int
    
    model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8"
    )

settings = Settings()