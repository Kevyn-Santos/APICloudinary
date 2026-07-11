import os
import sys
from unittest.mock import MagicMock

# Setup compartilhado por toda a suíte: credenciais e cloudinary mockados
# ANTES de qualquer import de src.* (Settings.py importa cloudinary no load).
os.environ.setdefault("CLOUD_NAME", "test_cloud")
os.environ.setdefault("API_KEY", "test_key")
os.environ.setdefault("API_SECRET", "test_secret")
sys.modules["cloudinary"] = MagicMock()
sys.modules["cloudinary.uploader"] = MagicMock()

import pytest #noqa: E402
from src.Core.security import rate_Limiter #noqa: E402


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    # Zera a contagem em memória do rate limiter antes e depois de cada teste,
    # evitando vazamento de estado entre testes (a rota /SendImage é limitada).
    rate_Limiter.reset()
    yield
    rate_Limiter.reset()
