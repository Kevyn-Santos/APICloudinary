import pytest
from fastapi import HTTPException
from src.Services.Upload import parse_images, uploadImage

# Setup de credenciais/cloudinary e reset do rate limiter ficam em tests/conftest.py

MB = 1024 * 1024


@pytest.fixture
def make_imagem(mocker):
    def _make(size_bytes: int, filenames: list[str], dir_name: str = "pasta_teste"):
        # parse_images filtra por img.file e lê imagem.sanitize_Name(),
        # então o mock precisa refletir esses atributos.
        upload_files = []
        for name in filenames:
            f = mocker.MagicMock()
            f.filename = name
            f.file = f"/tmp/{name}" if name else None
            upload_files.append(f)

        imagem = mocker.MagicMock()
        imagem.Image = upload_files
        imagem.size_image = mocker.AsyncMock(return_value=size_bytes)
        imagem.sanitize_Name = mocker.MagicMock(return_value=dir_name)
        imagem.dirName = dir_name
        return imagem
    return _make


# ── parse_images ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_parse_images_retorna_tuple_filepaths_e_dirname(make_imagem):
    imagem = make_imagem(5 * MB, ["foto1.jpg", "foto2.jpg", "foto3.jpg"])

    file_paths, dir_name = await parse_images(imagem)

    assert isinstance(file_paths, list)
    assert len(file_paths) == 3
    assert all("foto" in p for p in file_paths) #type: ignore
    assert dir_name == "pasta_teste"


@pytest.mark.asyncio
async def test_parse_images_filtra_arquivos_vazios(make_imagem):
    # name "" gera img.file None, que é filtrado por `if img.file`
    imagem = make_imagem(5 * MB, ["foto1.jpg", "", "foto3.jpg"])

    file_paths, _ = await parse_images(imagem)

    assert len(file_paths) == 2


@pytest.mark.asyncio
async def test_parse_images_mais_de_5_imagens_levanta_httperror(make_imagem):
    imagem = make_imagem(1 * MB, ["a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg", "f.jpg"])

    with pytest.raises(HTTPException) as exc_info:
        await parse_images(imagem)

    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_parse_images_imagem_acima_100mb_levanta_httperror(make_imagem):
    imagem = make_imagem(101 * MB, ["pesada.jpg"])

    with pytest.raises(HTTPException) as exc_info:
        await parse_images(imagem)

    assert exc_info.value.status_code == 422


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


# ── uploadImage ──────────────────────────────────────────────────────────────

def test_upload_image_chama_cloudinary_com_parametros_corretos(mocker):
    mock_upload = mocker.patch("src.Services.Upload.upload")
    mock_upload.return_value = {"secure_url": "https://res.cloudinary.com/test/image.jpg"}

    uploadImage("/tmp/foto.jpg", "minha_pasta")

    mock_upload.assert_called_once_with(
        "/tmp/foto.jpg",
        use_filename=mocker.ANY,
        unique_filename=mocker.ANY,
        overwrite=mocker.ANY,
        asset_folder="minha_pasta"
    )


def test_upload_image_retorna_secure_url(mocker):
    mock_upload = mocker.patch("src.Services.Upload.upload")
    url = "https://res.cloudinary.com/test/img.jpg"
    mock_upload.return_value = {"secure_url": url}

    resultado = uploadImage("/tmp/foto.jpg", "pasta")

    assert resultado == url
    assert isinstance(resultado, str)
