#Importação da bibioteca FASTAPI e suas dependencias
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.Core.Settings import configs
from src.Routes import Send


app = FastAPI(
    title=configs.PROJECT_NAME,
    description=configs.DESCRIPTION
) # Cria a instancia do Fastapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=configs.sanatize_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(Send.router)