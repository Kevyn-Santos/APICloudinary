from pydantic import BaseModel
from fastapi import UploadFile
from re import sub

class imagem(BaseModel):
    Image: list[UploadFile]
    ImageName: str
    
    def sanatize_Name(self):
        self.ImageName = sub(r'\s+', '_', sub(r'\d+', '', self.ImageName)).lower().strip('_')