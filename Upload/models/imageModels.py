from pydantic import BaseModel
from fastapi import UploadFile
from re import sub

class Imagem(BaseModel):
    Image: list[UploadFile]
    dirName: str
    
    def sanatize_Name(self):
        self.dirName = sub(r'\s+', '_', sub(r'\d+', '', self.dirName)).lower().strip('_')
    
    async def size_image(self) -> int:
        if not self.Image:
            raise ValueError("Sem imagens para tratar")
        else:
            for item in self.Image:
                imageBytes= await item.read()
                await item.seek(0)
                return len(imageBytes)
        return 0
