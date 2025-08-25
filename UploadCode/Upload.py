# importação da biblioteca do cloudinary junto com suas dependencias principais
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
# Importação de bibliotecas adicionais para manipulação de arquivos em sistema
from dotenv import load_dotenv
import os

load_dotenv() # Carrega as variaveis de ambiente

#configurações principais do cloudinary a aprtir da variavel de ambiente
cloudinary.config(
    cloud_name = os.getenv('CLOUD_NAME'),
    api_key = os.getenv('API_KEY'),
    api_secret =  os.getenv('API_SECRET'),
    secure = True
)

# Principal função que executa o upload de arquivos para o cloudinary
def uploadImagem(caminho: str, Pasta: str):

    # Faz o upload utilizando os métodos prioprios da biblioteca
    upload_result = cloudinary.uploader.upload( 
        caminho,
        use_filename = True,
        unique_filename= False,
        overwrite = True,
        asset_folder = Pasta,
        media_metadata = True,
        )
     
    URL = upload_result['secure_url']
    pasta = upload_result['asset_folder']
    return URL, pasta