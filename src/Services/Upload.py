# importação da biblioteca do cloudinary junto das suas dependencias principais
from cloudinary.uploader import upload

# Importação de bibliotecas adicionais para manipulação de arquivos em sistema
from src.Core.Settings import configs
from src.models.imageModels import Imagem

from fastapi import HTTPException
import os
from collections import UserList

#configurações principais do cloudinary a aprtir da variavel de ambiente
#cloudinary.config(
#    cloud_name = configs.CLOUD_NAME,
#    api_key = configs.API_KEY,
#    api_secret =  configs.API_SECRET,
#    secure = True
#)

async def parse_images(imagem: Imagem):

    if len(imagem.Image) > configs.LIMITE_IMAGENS:
        raise HTTPException(500, "Você pode enviar no máximo 5 imagens.")
    elif await imagem.size_image() > 100 * 1024 * 1024:
        raise HTTPException(500, "As imagens não podem exceder 100MB")
    else:
        fileName = [nomes.filename for nomes in imagem.Image if nomes.filename]
        filePath = [os.path.join(configs.UPLOAD_FOLDER, nome) for nome in fileName]
        
        return filePath, imagem.dirName


# Principal função que executa o upload de arquivos para o cloudinary
def uploadImage(caminho: str, Pasta: str) -> list[str]: # Caminho = Filepath

    # Faz o upload utilizando os métodos próprios da biblioteca
    upload_result: dict[str, str] = upload( 
        caminho,
        use_filename = configs.USE_FILENAME,
        unique_filename= configs.UNIQUE_FILENAME,
        overwrite = configs.OVERWRITE,
        asset_folder = Pasta,
        media_metadata = configs.MEDIA_METADATA,
        )
     
    # URL = upload_result['secure_url']
    return list(upload_result['secure_url'])