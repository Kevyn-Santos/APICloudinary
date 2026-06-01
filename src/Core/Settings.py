from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (AnyUrl, BeforeValidator, computed_field)
from cloudinary import config
from typing import Annotated, Any

# limpa os IP's que virão de CORS
def cors_config(Urls: Any) -> list[str]: #type: ignore
    if isinstance(Urls, list):
        return[str(u).strip() for u in Urls] # Se for lista, retira os espaços
    
    if isinstance(Urls, str):
        clean = Urls.strip().strip('[]')
        return[u.strip() for u in clean.split(',') if u.strip()] # Se forem strings, retira os colchetes e espaços, depois separa por virgula
    else: 
        ValueError(Urls)

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file='../.env',
        env_ignore_empty=False
    )

    PROJECT_NAME: str ='Cloudinary Image Sender'
    DESCRIPTION: str= 'A modular API builded to send images to cloudinary'

    LIMITE_IMAGENS: int = 5
    LIMITE_TEMPO: int = 10

    CLOUD_NAME: str
    API_KEY: str
    API_SECRET: str

    HOSTS: Annotated[list[AnyUrl] | str, BeforeValidator(cors_config)] = []
    COMMONS_URLS:list[str] = ["http://localhost","http://localhost:5500","http://127.0.0.1","http://127.0.0.1:5500","http://127.0.0.1:8000"]

    @computed_field
    @property
    def sanatize_cors(self) -> list[str]:
        return [str(origins) for origins in self.HOSTS] + self.COMMONS_URLS # type: ignore
    

    USE_FILENAME: bool=True
    UNIQUE_FILENAME: bool= False
    OVERWRITE: bool=True
    MEDIA_METADATA: bool=True   

    

configs = Settings() #type: ignore
config(
cloud_name = configs.CLOUD_NAME,
api_key = configs.API_KEY,
api_secret =  configs.API_SECRET,
secure = True
)