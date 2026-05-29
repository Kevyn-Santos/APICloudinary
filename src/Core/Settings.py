from pydantic_settings import BaseSettings, SettingsConfigDict
from cloudinary import config

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file='./.env',
        env_ignore_empty=False
    )

    PROJECT_NAME: str ='Cloudinary Image Sender'
    DESCRIPTION: str= 'A modular API builded to send images to cloudinary'

    UPLOAD_FOLDER: str = '/tmp'
    LIMITE_IMAGENS: int = 5

    CLOUD_NAME: str
    API_KEY: str
    API_SECRET: str


    USE_FILENAME: bool | bool=True
    UNIQUE_FILENAME: bool | bool= False
    OVERWRITE: bool | bool=True
    MEDIA_METADATA: bool | bool=True

    

configs = Settings() #type: ignore
config(
cloud_name = configs.CLOUD_NAME,
api_key = configs.API_KEY,
api_secret =  configs.API_SECRET,
secure = True
)