# Rate limiter da API: limita envios por IP usando slowapi.
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from fastapi import Request
from fastapi.responses import JSONResponse

from src.Core.Settings import configs

# Limiter que identifica o solicitante pelo IP de origem.
rate_Limiter = Limiter(key_func=get_remote_address)

# Janela do limite: LIMITE_IMAGENS requisições a cada LIMITE_TEMPO segundos.
LIMITE_ENVIOS = f"{configs.LIMITE_IMAGENS}/{configs.LIMITE_TEMPO} seconds"


def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    # Resposta padronizada quando o limite de envios é excedido.
    return JSONResponse(
        status_code=429,
        content={
            "status code": 429,
            "message": "Limite de envios atingido, tente novamente em alguns segundos",
        },
    )
