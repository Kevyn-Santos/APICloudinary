#Importação da bibioteca FASTAPI e suas dependencias
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.Core.Settings import configs
from src.Routes import Send

# Bibliotecas para manipulação de arquivos de sistema
import os


app = FastAPI(
    title=configs.PROJECT_NAME,
    description=configs.DESCRIPTION
) # Cria a instancia do Fastapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
os.makedirs(configs.UPLOAD_FOLDER, exist_ok = True) # Cria uma pasta para armazenar as imagens

app.include_router(Send.router)