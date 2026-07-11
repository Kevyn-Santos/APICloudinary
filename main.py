#Importação da bibioteca FASTAPI e suas dependencias
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi.errors import RateLimitExceeded

from src.Core.Settings import configs
from src.Core.security import rate_Limiter, rate_limit_handler
from src.Routes import Send


app = FastAPI(
    title=configs.PROJECT_NAME,
    description=configs.DESCRIPTION
) # Cria a instancia do Fastapi

# Registra o rate limiter e o handler de excesso de envios (HTTP 429)
app.state.limiter = rate_Limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler) # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins= "*" if configs.DEBUG else configs.sanatize_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(Send.router)