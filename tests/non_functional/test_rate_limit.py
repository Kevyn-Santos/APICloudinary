import time
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from main import app
from src.Core.Settings import configs

# Setup de credenciais/cloudinary e reset do rate limiter ficam em tests/conftest.py

# raise_server_exceptions=False: exceções do servidor viram respostas HTTP
client = TestClient(app, raise_server_exceptions=False)

FAKE_URL = "https://res.cloudinary.com/test/image/upload/v1/pasta/foto.jpg"
MENSAGEM_LIMITE = "Limite de envios atingido, tente novamente em alguns segundos"


@pytest.fixture
def mock_envio_imagens(mocker):
    # Simula um envio bem-sucedido sem tocar no Cloudinary: parse_images (async)
    # e uploadImage são substituídos por mocks.
    mocker.patch(
        "src.Routes.Send.parse_images",
        new=AsyncMock(return_value=(["fake_path"], "pasta")),
    )
    mocker.patch("src.Routes.Send.uploadImage", return_value=FAKE_URL)


def test_spam_envio_atinge_429(mock_envio_imagens):
    """
    Teste de spam: envia LIMITE_IMAGENS + 1 requisições de envio em sequência.
    As primeiras LIMITE_IMAGENS devem retornar 200; a requisição excedente deve
    retornar 429 com a mensagem padronizada de limite atingido.
    """
    limite = configs.LIMITE_IMAGENS
    relatorio = []

    for i in range(limite + 1):
        momento = datetime.now().isoformat(timespec="milliseconds")
        inicio = time.monotonic()
        response = client.post(
            "/SendImage",
            files={"Image": (f"foto_{i}.jpg", b"fake image content", "image/jpeg")},
            data={"dirName": "pasta"},
        )
        relatorio.append({
            "requisicao": i + 1,
            "http": response.status_code,
            "erro": response.json() if response.status_code != 200 else None,
            "momento": momento,
            "duracao_ms": round((time.monotonic() - inicio) * 1000, 2),
        })

    # Relatório exigido: código HTTP, erro retornado e momento de cada requisição
    print("\n--- Relatório do teste de spam ---")
    for linha in relatorio:
        print(linha)

    # As primeiras LIMITE_IMAGENS requisições passam (200)
    for linha in relatorio[:limite]:
        assert linha["http"] == 200, f"Requisição {linha['requisicao']} deveria ser 200"

    # A requisição excedente é bloqueada (429) com a mensagem padronizada
    excedente = relatorio[limite]
    assert excedente["http"] == 429
    assert excedente["erro"] == {"status code": 429, "message": MENSAGEM_LIMITE}
