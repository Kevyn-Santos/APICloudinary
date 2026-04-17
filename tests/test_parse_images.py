import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

# ── Variáveis de ambiente para testes ────────────────────────────────────────
# Definidas antes do import de Services.Upload para que Settings() não falhe
# por ausência das credenciais reais.
os.environ.setdefault("CLOUD_NAME", "test_cloud")
os.environ.setdefault("API_KEY", "test_api_key")
os.environ.setdefault("API_SECRET", "test_api_secret")

# ── Mock do cloudinary ────────────────────────────────────────────────────────
# cloudinary.uploader faz chamadas de rede na inicialização do módulo.
sys.modules["cloudinary"] = MagicMock()
sys.modules["cloudinary.uploader"] = MagicMock()

# ── Import do módulo testado ──────────────────────────────────────────────────
from Services.Upload import parse_images  # noqa: E402
from fastapi import HTTPException          # noqa: E402

MB = 1024 * 1024


def make_imagem(size_bytes: int, filenames: list[str]) -> MagicMock:
    upload_files = [MagicMock(filename=name) for name in filenames]
    imagem = MagicMock()
    imagem.Image = upload_files
    imagem.size_image = AsyncMock(return_value=size_bytes)
    return imagem


class TestParseImages(unittest.IsolatedAsyncioTestCase):

    async def test_retorna_lista_de_nomes_tres_imagens(self):
        """Envio válido: 3 imagens abaixo de 100MB."""
        imagem = make_imagem(5 * MB, ["foto1.jpg", "foto2.jpg", "foto3.jpg"])

        resultado = await parse_images(imagem)

        print("\n--- Nomes retornados (3 imagens válidas) ---")
        for nome in resultado:
            print(f"  {nome}")

        self.assertEqual(resultado, ["foto1.jpg", "foto2.jpg", "foto3.jpg"])

    async def test_retorna_lista_de_nomes_cinco_imagens(self):
        """Envio válido: 5 imagens abaixo de 100MB."""
        imagem = make_imagem(10 * MB, ["a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg"])

        resultado = await parse_images(imagem)

        print("\n--- Nomes retornados (5 imagens válidas) ---")
        for nome in resultado:
            print(f"  {nome}")

        self.assertEqual(len(resultado), 5)

    async def test_erro_mais_de_cinco_imagens(self):
        """Mais de 5 imagens deve levantar HTTPException 500."""
        imagem = make_imagem(1 * MB, ["a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg", "f.jpg"])

        print("\n--- Erro: mais de 5 imagens ---")
        with self.assertRaises(HTTPException) as ctx:
            await parse_images(imagem)

        print(f"  HTTPException {ctx.exception.status_code}: {ctx.exception.detail}")
        self.assertEqual(ctx.exception.status_code, 500)

    async def test_erro_imagem_acima_de_100mb(self):
        """Imagem acima de 100MB deve levantar HTTPException 500."""
        imagem = make_imagem(101 * MB, ["pesada.jpg", "pesada2.jpg"])

        print("\n--- Erro: imagem acima de 100MB ---")
        with self.assertRaises(HTTPException) as ctx:
            await parse_images(imagem)

        print(f"  HTTPException {ctx.exception.status_code}: {ctx.exception.detail}")
        self.assertEqual(ctx.exception.status_code, 500)

    async def test_imagem_exatamente_100mb_e_aceita(self):
        """Imagem com exatamente 100MB deve ser aceita (limite é exclusivo)."""
        imagem = make_imagem(100 * MB, ["limite.jpg", "limite2.jpg"])

        resultado = await parse_images(imagem)

        print("\n--- Imagem no limite exato de 100MB ---")
        for nome in resultado:
            print(f"  {nome}")

        self.assertIsInstance(resultado, list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
