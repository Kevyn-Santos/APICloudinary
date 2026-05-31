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
from fastapi import HTTPException
from src.Services.Upload import parse_images, uploadImage

MB = 1024 * 1024


@pytest.fixture
def make_imagem(mocker):
    def _make(size_bytes: int, filenames: list[str], dir_name: str = "pasta_teste"):
        upload_files = [mocker.MagicMock(filename=name) for name in filenames]
        imagem = mocker.MagicMock()
        imagem.Image = upload_files
        imagem.size_image = mocker.AsyncMock(return_value=size_bytes)
        imagem.dirName = dir_name
        return imagem
    return _make


# ── parse_images ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_parse_images_retorna_tuple_filepaths_e_dirname(make_imagem):
    imagem = make_imagem(5 * MB, ["foto1.jpg", "foto2.jpg", "foto3.jpg"])

    file_paths, dir_name = await parse_images(imagem)

    assert isinstance(file_paths, list)
    assert len(file_paths) == 3
    assert all("foto" in p for p in file_paths)
    assert dir_name == "pasta_teste"


@pytest.mark.asyncio
async def test_parse_images_filtra_filenames_vazios(make_imagem):
    imagem = make_imagem(5 * MB, ["foto1.jpg", "", "foto3.jpg"])
    # Ajusta manualmente: o mock com filename="" deve ser filtrado
    imagem.Image[1].filename = ""

    file_paths, _ = await parse_images(imagem)

    assert len(file_paths) == 2


@pytest.mark.asyncio
async def test_parse_images_mais_de_5_imagens_levanta_httperror(make_imagem):
    imagem = make_imagem(1 * MB, ["a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg", "f.jpg"])

    with pytest.raises(HTTPException) as exc_info:
        await parse_images(imagem)

    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_parse_images_imagem_acima_100mb_levanta_httperror(make_imagem):
    imagem = make_imagem(101 * MB, ["pesada.jpg"])

    with pytest.raises(HTTPException) as exc_info:
        await parse_images(imagem)

    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_parse_images_exatamente_100mb_e_aceito(make_imagem):
    imagem = make_imagem(100 * MB, ["limite.jpg", "limite2.jpg"])

    result = await parse_images(imagem)

    assert result is not None


@pytest.mark.asyncio
async def test_parse_images_exatamente_5_imagens_e_aceito(make_imagem):
    imagem = make_imagem(5 * MB, ["a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg"])

    file_paths, _ = await parse_images(imagem)

    assert len(file_paths) == 5


# ── uploadImage ────────────────────────────────────────────────────────────────

def test_upload_image_chama_cloudinary_com_parametros_corretos(mocker):
    mock_upload = mocker.patch("src.Services.Upload.upload")
    mock_upload.return_value = {"secure_url": "https://res.cloudinary.com/test/image.jpg"}

    uploadImage("/tmp/foto.jpg", "minha_pasta")

    mock_upload.assert_called_once_with(
        "/tmp/foto.jpg",
        use_filename=mocker.ANY,
        unique_filename=mocker.ANY,
        overwrite=mocker.ANY,
        asset_folder="minha_pasta",
        media_metadata=mocker.ANY,
    )


def test_upload_image_retorna_lista_de_chars_da_url(mocker):
    """Documenta comportamento atual: list(url) retorna lista de caracteres."""
    mock_upload = mocker.patch("src.Services.Upload.upload")
    url = "https://res.cloudinary.com/test/img.jpg"
    mock_upload.return_value = {"secure_url": url}

    resultado = uploadImage("/tmp/foto.jpg", "pasta")

    # Comportamento atual: string → lista de caracteres (bug conhecido)
    assert resultado == list(url)
    assert isinstance(resultado, list)
    assert resultado[0] == "h"
