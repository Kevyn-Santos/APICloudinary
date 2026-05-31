from pydantic import BaseModel
from fastapi import UploadFile
from re import sub

class Imagem(BaseModel):
    Image: list[UploadFile]
    dirName: str

    def sanitize_Name(self):
        self.dirName = sub(r'\s+', '_', sub(r'\d+', '', self.dirName)).lower().strip('_')
        return self.dirName
    
    async def size_image(self) -> int:
        if not self.Image:
            raise ValueError("Sem imagens para tratar")
        return sum(image.size or 0 for image in self.Image)
