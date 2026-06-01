import pytest
from fastapi.testclient import TestClient
from main import app

# Setup de credenciais/cloudinary e reset do rate limiter ficam em tests/conftest.py

# raise_server_exceptions=False: exceções do servidor viram respostas HTTP
# em vez de propagar para os testes — necessário para testar erros internos.
client = TestClient(app, raise_server_exceptions=False)

FAKE_URL = "https://res.cloudinary.com/test/image/upload/v1/pasta/foto.jpg"


@pytest.fixture(autouse=True)
def mock_cloudinary_upload(mocker):
    mock = mocker.patch("src.Services.Upload.upload")
    mock.return_value = {"secure_url": FAKE_URL}
    return mock


# ── Testes de integração: POST /SendImage ────────────────────────────────────

def test_sendimage_endpoint_existe():
    """O endpoint /SendImage está registrado no app."""
    routes = [getattr(r, "path", None) for r in app.routes]
    assert "/SendImage" in routes


def test_sendimage_aceita_multipart_e_retorna_links():
    """Envio multipart com uma imagem retorna 200 e a secure_url do Cloudinary."""
    response = client.post(
        "/SendImage",
        files={"Image": ("foto.jpg", b"fake image content", "image/jpeg")},
        data={"dirName": "minha pasta"},
    )
    assert response.status_code == 200
    assert response.json() == {"Link das imagens": [FAKE_URL]}


def test_sendimage_multiplas_imagens_retorna_uma_url_por_imagem():
    """Várias imagens no mesmo campo retornam uma URL por imagem."""
    response = client.post(
        "/SendImage",
        files=[
            ("Image", ("a.jpg", b"img a", "image/jpeg")),
            ("Image", ("b.jpg", b"img b", "image/jpeg")),
            ("Image", ("c.jpg", b"img c", "image/jpeg")),
        ],
        data={"dirName": "galeria fotos"},
    )
    assert response.status_code == 200
    assert response.json() == {"Link das imagens": [FAKE_URL, FAKE_URL, FAKE_URL]}


def test_sendimage_rejeita_json_com_422():
    """
    A rota usa Form(multipart/form-data); um corpo JSON não fornece os campos
    de formulário esperados e é rejeitado na validação com 422.
    """
    response = client.post("/SendImage", json={"Image": [], "dirName": "pasta"})
    assert response.status_code == 422
