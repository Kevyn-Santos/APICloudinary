# importação da biblioteca do cloudinary junto das suas dependencias principais
from cloudinary.uploader import upload

# Importação de bibliotecas adicionais para manipulação de arquivos em sistema
from src.Core.Settings import configs
from src.models.imageModels import Imagem

from fastapi import HTTPException
from typing import Any
import os

async def parse_images(imagem: Imagem):
    os.makedirs(configs.UPLOAD_FOLDER, exist_ok = True) # Cria uma pasta para armazenar as imagens
    
    if len(imagem.Image) > configs.LIMITE_IMAGENS:
        raise HTTPException(422, "Você pode enviar no máximo 5 imagens.")
    elif await imagem.size_image() > 100 * 1024 * 1024:
        raise HTTPException(422, "As imagens não podem exceder 100MB")
    else:
        # fileName = [nomes.filename for nomes in imagem.Image if nomes.filename]
        file = [img.file for img in imagem.Image if img.file]
        
        return file, imagem.sanitize_Name()


# Principal função que executa o upload de arquivos para o cloudinary
def uploadImage(caminho: Any, Pasta: str):

    print(f"""
          \n\nCaminho recebido: {caminho}({type(caminho)}), 
          pasta recebida: {Pasta}({type(Pasta)})\n\n""")

    # Faz o upload utilizando os métodos próprios da biblioteca
    upload_result: dict[str, str] = upload( 
        caminho,
        use_filename = configs.USE_FILENAME,
        unique_filename= configs.UNIQUE_FILENAME,
        overwrite = configs.OVERWRITE,
        asset_folder = Pasta,
        media_metadata = configs.MEDIA_METADATA,
        )

    return upload_result['secure_url']