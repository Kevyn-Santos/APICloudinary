from fastapi import APIRouter, Form
from src.models.imageModels import Imagem
from src.Services.Upload import parse_images, uploadImage
from typing import Annotated

router = APIRouter(tags=['SendImages'])

@router.post('/SendImage')
async def send_Image(image: Annotated[Imagem, Form(media_type="multipart/form-data")]):
    file_paths, dir_names = await parse_images(image)
    links = [uploadImage(imagePath, dirName) for imagePath, dirName in zip(file_paths, dir_names)]
    return {'Link das imagens': links}
        
     