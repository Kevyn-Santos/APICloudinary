import pytest
from src.models.imageModels import Imagem

# Setup de credenciais/cloudinary e reset do rate limiter ficam em tests/conftest.py


@pytest.fixture
def make_upload_file(mocker):
    def _make(size: int, filename: str):
        mock = mocker.MagicMock()
        mock.filename = filename
        mock.size = size
        return mock
    return _make


# ── sanitize_Name ────────────────────────────────────────────────────────────

def test_sanitize_remove_numeros():
    imagem = Imagem.model_construct(Image=[], dirName="pasta123")
    imagem.sanitize_Name()
    assert imagem.dirName == "pasta"


def test_sanitize_substitui_espacos_por_underscore():
    imagem = Imagem.model_construct(Image=[], dirName="minha pasta")
    imagem.sanitize_Name()
    assert imagem.dirName == "minha_pasta"


def test_sanitize_converte_para_minusculo():
    imagem = Imagem.model_construct(Image=[], dirName="PASTA_TESTE")
    imagem.sanitize_Name()
    assert imagem.dirName == "pasta_teste"


def test_sanitize_nome_misto():
    # "Fotos 2024 Viagem" → remove "2024" → "Fotos  Viagem" → \s+ colapsa → "fotos_viagem"
    imagem = Imagem.model_construct(Image=[], dirName="Fotos 2024 Viagem")
    imagem.sanitize_Name()
    assert imagem.dirName == "fotos_viagem"


def test_sanitize_remove_underscore_das_pontas():
    # Espaços nas pontas viram "_" e são removidos pelo strip('_') final
    imagem = Imagem.model_construct(Image=[], dirName=" pasta ")
    imagem.sanitize_Name()
    assert imagem.dirName == "pasta"


# ── size_image ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_size_image_soma_tamanho_de_todas_imagens(make_upload_file):
    imagens = [
        make_upload_file(1024, "foto1.jpg"),
        make_upload_file(2048, "foto2.jpg"),
    ]
    imagem = Imagem.model_construct(Image=imagens, dirName="galeria")

    tamanho = await imagem.size_image()

    assert tamanho == 1024 + 2048


@pytest.mark.asyncio
async def test_size_image_sem_imagens_levanta_value_error():
    imagem = Imagem.model_construct(Image=[], dirName="galeria")

    with pytest.raises(ValueError, match="Sem imagens para tratar"):
        await imagem.size_image()


@pytest.mark.asyncio
async def test_size_image_lista_com_uma_imagem(make_upload_file):
    imagens = [make_upload_file(512, "unica.jpg")]
    imagem = Imagem.model_construct(Image=imagens, dirName="pasta")

    tamanho = await imagem.size_image()

    assert tamanho == 512


@pytest.mark.asyncio
async def test_size_image_imagem_sem_size_conta_como_zero(make_upload_file):
    # image.size None (UploadFile sem tamanho conhecido) é tratado como 0
    imagens = [make_upload_file(None, "sem_size.jpg"), make_upload_file(256, "ok.jpg")]
    imagem = Imagem.model_construct(Image=imagens, dirName="pasta")

    tamanho = await imagem.size_image()

    assert tamanho == 256
