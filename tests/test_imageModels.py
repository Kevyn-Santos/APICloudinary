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
from src.models.imageModels import Imagem


@pytest.fixture
def make_upload_file(mocker):
    def _make(content: bytes, filename: str):
        mock = mocker.MagicMock()
        mock.filename = filename
        mock.read = mocker.AsyncMock(return_value=content)
        mock.seek = mocker.AsyncMock(return_value=None)
        return mock
    return _make


# ── sanatize_Name ──────────────────────────────────────────────────────────────

def test_sanatize_remove_numeros():
    imagem = Imagem.model_construct(Image=[], dirName="pasta123")
    imagem.sanatize_Name()
    assert imagem.dirName == "pasta"


def test_sanatize_substitui_espacos_por_underscore():
    imagem = Imagem.model_construct(Image=[], dirName="minha pasta")
    imagem.sanatize_Name()
    assert imagem.dirName == "minha_pasta"


def test_sanatize_converte_para_minusculo():
    imagem = Imagem.model_construct(Image=[], dirName="PASTA_TESTE")
    imagem.sanatize_Name()
    assert imagem.dirName == "pasta_teste"


def test_sanatize_nome_misto():
    # "Fotos 2024 Viagem" → remove "2024" → "Fotos  Viagem" → \s+ colapsa → "fotos_viagem"
    imagem = Imagem.model_construct(Image=[], dirName="Fotos 2024 Viagem")
    imagem.sanatize_Name()
    assert imagem.dirName == "fotos_viagem"


def test_sanatize_remove_underscore_das_pontas():
    imagem = Imagem.model_construct(Image=[], dirName="123pasta")
    imagem.sanatize_Name()
    assert imagem.dirName == "pasta"


# ── size_image ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_size_image_retorna_tamanho_da_primeira_imagem(make_upload_file):
    imagens = [
        make_upload_file(b"A" * 1024, "foto1.jpg"),
        make_upload_file(b"B" * 2048, "foto2.jpg"),
    ]
    imagem = Imagem.model_construct(Image=imagens, dirName="galeria")

    tamanho = await imagem.size_image()

    assert tamanho == 1024


@pytest.mark.asyncio
async def test_size_image_sem_imagens_levanta_value_error():
    imagem = Imagem.model_construct(Image=[], dirName="galeria")

    with pytest.raises(ValueError, match="Sem imagens para tratar"):
        await imagem.size_image()


@pytest.mark.asyncio
async def test_size_image_lista_com_uma_imagem(make_upload_file):
    imagens = [make_upload_file(b"X" * 512, "unica.jpg")]
    imagem = Imagem.model_construct(Image=imagens, dirName="pasta")

    tamanho = await imagem.size_image()

    assert tamanho == 512


@pytest.mark.asyncio
async def test_size_image_chama_seek_apos_read(make_upload_file):
    upload_file = make_upload_file(b"Z" * 100, "img.jpg")
    imagem = Imagem.model_construct(Image=[upload_file], dirName="pasta")

    await imagem.size_image()

    upload_file.seek.assert_called_once_with(0)
