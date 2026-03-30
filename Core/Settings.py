from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file='../.env',
        env_ignore_empty=False
    )

    UPLOAD_FOLDER = '/tmp'
    LIMITE_IMAGENS = 5

    CLOUD_NAME: str
    API_KEY: str
    API_SECRET: str

    USE_FILENAME: bool | bool=True
    UNIQUE_FILENAME: bool | bool= False
    OVERWRITE: bool | bool=True
    MEDIA_METADATA: bool | bool=True

configs = Settings() #type: ignore