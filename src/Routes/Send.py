from fastapi import APIRouter, UploadFile
from src.models.imageModels import Imagem
from src.Services.Upload import parse_images, uploadImage

router = APIRouter(tags=['SendImages'])

@router.post('/SendImage')
async def send_Image(image: Imagem):
    file_paths, dir_names = await parse_images(image)
    links = [uploadImage(imagePath, dirName) for imagePath, dirName in zip(file_paths, dir_names)]
    return {'Link das imagens': links}
        
     