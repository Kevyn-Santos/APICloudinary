from fastapi import APIRouter, Form, Request
from src.models.imageModels import Imagem
from src.Services.Upload import parse_images, uploadImage
from src.Core.security import rate_Limiter, LIMITE_ENVIOS
from typing import Annotated

router = APIRouter(tags=['SendImages'])

@router.post('/SendImage')
@rate_Limiter.limit(LIMITE_ENVIOS)
async def send_Image(request: Request, image: Annotated[Imagem, Form(media_type="multipart/form-data")]):
    file_paths, dir_names = await parse_images(image)
    links = [uploadImage(imagePath, dir_names) for imagePath, _ in zip(file_paths, dir_names)]
    return {'Link das imagens': links}
        
     