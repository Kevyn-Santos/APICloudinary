import unittest
from unittest.mock import AsyncMock, MagicMock

from Upload.models.imageModels import Imagem


def make_upload_file(content: bytes, filename: str) -> MagicMock:
    mock = MagicMock()
    mock.filename = filename
    mock.read = AsyncMock(return_value=content)
    mock.seek = AsyncMock(return_value=None)
    return mock


class TestSizeImage(unittest.IsolatedAsyncioTestCase):

    async def test_size_image_retorna_tamanho_por_imagem(self):
        imagens = [
            make_upload_file(b"X" * 1024, "imagem1.jpg"),
            make_upload_file(b"Y" * 2048, "imagem2.jpg"),
            make_upload_file(b"Z" * 512,  "imagem3.jpg"),
            make_upload_file(b"W" * 4096, "imagem4.jpg"),
            make_upload_file(b"V" * 768,  "imagem5.jpg"),
        ]

        imagem = Imagem.model_construct(Image=imagens, dirName="pasta_teste")

        print("\n--- Tamanho das imagens ---")
        for upload_file in imagem.Image:
            conteudo = await upload_file.read()
            await upload_file.seek(0)
            tamanho = len(conteudo)
            print(f"  {upload_file.filename}: {tamanho} bytes")
            self.assertIsInstance(tamanho, int)
            self.assertGreater(tamanho, 0)

    async def test_size_image_sem_imagens_levanta_erro(self):
        imagem = Imagem.model_construct(Image=[], dirName="pasta_teste")

        print("\n--- Resultado sem imagens ---")
        with self.assertRaises(ValueError) as ctx:
            await imagem.size_image()
        print(f"  ValueError: {ctx.exception}")

    async def test_size_image_tres_imagens(self):
        imagens = [
            make_upload_file(b"A" * 300, "foto1.png"),
            make_upload_file(b"B" * 600, "foto2.png"),
            make_upload_file(b"C" * 900, "foto3.png"),
        ]

        imagem = Imagem.model_construct(Image=imagens, dirName="galeria")

        print("\n--- Tamanho com 3 imagens ---")
        for upload_file in imagem.Image:
            conteudo = await upload_file.read()
            await upload_file.seek(0)
            tamanho = len(conteudo)
            print(f"  {upload_file.filename}: {tamanho} bytes")
            self.assertIsInstance(tamanho, int)
            self.assertGreater(tamanho, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
