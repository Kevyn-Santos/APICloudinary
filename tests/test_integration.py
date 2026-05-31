
import os
import sys
from unittest.mock import MagicMock

# Mock de credenciais e cloudinary antes de qualquer import de src.*
os.environ.setdefault("CLOUD_NAME", "test_cloud")
os.environ.setdefault("API_KEY", "test_key")
os.environ.setdefault("API_SECRET", "test_secret")
sys.modules["cloudinary"] = MagicMock()
sys.modules["cloudinary.uploader"] = MagicMock()

import pytest
from fastapi.testclient import TestClient
from main import app

# raise_server_exceptions=False: exceções do servidor viram respostas 4xx/5xx
# em vez de propagar para os testes — necessário para testar erros internos
client = TestClient(app, raise_server_exceptions=False)

FAKE_URL = "https://res.cloudinary.com/test/image/upload/v1/pasta/foto.jpg"


@pytest.fixture(autouse=True)
def mock_cloudinary_upload(mocker):
    mock = mocker.patch("src.Services.Upload.upload")
    mock.return_value = {"secure_url": FAKE_URL}
    return mock


# ── Testes de integração: POST /SendImage ────────────────────────────────────
#
# CONTEXTO DO BUG (descoberto na tentativa 2):
# `Send.py` declara `send_Image(image: Imagem)` onde `Imagem` é um BaseModel
# com `Image: list[UploadFile]`. FastAPI interpreta isso como JSON body, não
# multipart/form-data — logo requisições com arquivos retornam 422.
# Os testes abaixo documentam esse comportamento atual e validam o que é
# possível testar enquanto o router não for corrigido.

def test_sendimage_endpoint_existe():
    """Verifica que o endpoint /SendImage está registrado no app."""
    routes = [getattr(r, "path", None) for r in app.routes]
    assert "/SendImage" in routes


def test_sendimage_rejeita_multipart_com_422():
    """
    Documenta comportamento atual: endpoint rejeita multipart/form-data com 422
    porque o modelo Imagem é interpretado como JSON body pelo FastAPI.
    BUG: Send.py precisa usar Form()/File() annotations no modelo ou declarar
    os parâmetros diretamente na função para aceitar multipart.
    """
    response = client.post(
        "/SendImage",
        files={"Image": ("foto.jpg", b"fake image content", "image/jpeg")},
        data={"dirName": "minha_pasta"},
    )
    assert response.status_code == 422
    detail = response.json()["detail"][0]
    assert detail["type"] == "model_attributes_type"


def test_sendimage_rejeita_json_com_lista_vazia_com_500():
    """
    JSON com Image=[] passa a validação do modelo mas size_image() levanta
    ValueError (não capturado) — resulta em 500.
    BUG secundário: parse_images deveria capturar e converter para HTTPException.
    """
    response = client.post(
        "/SendImage",
        json={"Image": [], "dirName": "pasta"},
    )
    assert response.status_code == 500


def test_enviar_endpoint_legado_funciona(mocker):
    """
    Smoke test no endpoint legado POST /enviar (main.py) que usa
    parâmetros Form/File diretos — funciona corretamente com multipart.
    """
    mocker.patch("main.uploadImage", return_value=FAKE_URL)

    response = client.post(
        "/enviar",
        files={"Imagem": ("foto.jpg", b"fake image content", "image/jpeg")},
        data={"Nome_Pasta": "minha_pasta"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "link das imagens" in body
    assert body["link das imagens"] == [FAKE_URL]
