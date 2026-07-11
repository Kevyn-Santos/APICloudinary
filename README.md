# APICloudinary

API REST em **FastAPI** para upload de imagens no **Cloudinary**. Recebe imagens via `multipart/form-data`, envia os arquivos diretamente da memória para o Cloudinary — sem salvar em disco — e retorna as `secure_url`s dos arquivos hospedados.

---

## Estrutura do projeto

```
APICloudinary/
├── main.py                        # Instância do FastAPI; registra rate limiter, CORS e o router de Send
├── Dockerfile                     # Build multi-stage (Python 3.12-alpine), usuário não-root, porta 8000
├── docker-compose.yml
├── requirements.txt
├── sample.env                     # Modelo de variáveis de ambiente
├── src/
│   ├── Core/
│   │   ├── Settings.py            # Configurações via pydantic-settings; configura o Cloudinary no load
│   │   └── security.py            # Rate limiter (slowapi) + handler HTTP 429
│   ├── models/
│   │   └── imageModels.py         # Model `Imagem` (Image, dirName) com sanitize_Name() e size_image()
│   ├── Services/
│   │   └── Upload.py              # parse_images() (validação) + uploadImage() (chamada ao Cloudinary)
│   └── Routes/
│       └── Send.py                # Endpoint POST /SendImage
├── tests/
│   ├── conftest.py                # Mock do cloudinary + reset do rate limiter
│   ├── test_integration.py        # Testes de integração via TestClient
│   ├── test_imageModels.py        # Testes unitários do model Imagem
│   ├── test_parse_images.py       # Testes unitários de parse_images() e uploadImage()
│   └── non_functional/
│       └── test_rate_limit.py     # Teste de spam: valida o HTTP 429
├── Assets/
│   ├── EnvioImagensJSON.html      # Formulário de envio; resultado redireciona para um JSON blob
│   └── EnvioImagensInScreen.html  # Formulário de envio com resultado exibido na própria página
└── misc/                          # Anotações e especificações internas do desenvolvimento
```

A arquitetura é modular e em camadas, com dependências correndo em uma única direção:

```
Routes → Services → models + Core
```

`Core` concentra a infraestrutura transversal (configuração e segurança) e é a única camada com acesso global; as demais só se comunicam para baixo na hierarquia.

---

## Bibliotecas utilizadas

| Biblioteca | Função no projeto |
|---|---|
| **FastAPI** | Framework web — roteamento, validação de requisições, serialização de respostas |
| **Uvicorn** | Servidor ASGI que executa a aplicação |
| **Pydantic / pydantic-settings** | Validação de modelos de dados e carregamento tipado de variáveis de ambiente |
| **cloudinary** | SDK oficial para upload e gerenciamento de arquivos no Cloudinary |
| **slowapi** | Rate limiting por IP, integrado ao FastAPI |
| **python-multipart** | Suporte ao recebimento de arquivos via `multipart/form-data` |
| **python-dotenv** | Carregamento de arquivos `.env` em desenvolvimento |
| **pytest / pytest-asyncio / pytest-mock** | Suíte de testes unitários, de integração e assíncronos |

---

## Ordem de execução de uma requisição

```
1. Cliente envia POST /SendImage
   └─ multipart/form-data: { Image: [arquivo(s)], dirName: "nome-da-pasta" }

2. Rate Limiter (slowapi)
   └─ Verifica LIMITE_IMAGENS requisições por LIMITE_TEMPO segundos, por IP
   └─ HTTP 429 se excedido

3. Route handler (src/Routes/Send.py)
   └─ Monta o objeto Imagem (model) a partir do form

4. parse_images() (src/Services/Upload.py)
   ├─ Valida a quantidade de arquivos (máx. 5)
   ├─ Valida o tamanho total (máx. 100 MB)
   └─ Sanitiza dirName (remove números/caracteres especiais, colapsa espaços em "_", minúsculas)

5. uploadImage() (src/Services/Upload.py) — executado para cada arquivo
   └─ Envia o arquivo ao Cloudinary via SDK, direto da memória (img.file)
   └─ Retorna a secure_url do arquivo hospedado

6. Resposta ao cliente
   └─ JSON: { "Link das imagens": ["https://...", ...] }
```

---

## Configuração

Todas as configurações — credenciais do Cloudinary, limites de rate e comportamento de upload — são definidas via variáveis de ambiente (arquivo `.env` na raiz do projeto). Use `sample.env` como modelo:

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `CLOUD_NAME` | Sim | — | Nome da conta Cloudinary |
| `API_KEY` | Sim | — | Chave de API da conta Cloudinary |
| `API_SECRET` | Sim | — | Secret da API da conta Cloudinary |
| `LIMITE_IMAGENS` | Não | `5` | Máximo de requisições por janela de tempo do rate limiter |
| `LIMITE_TEMPO` | Não | `10` | Janela de tempo (segundos) do rate limiter |
| `HOSTS` | Não | `[]` | Origens CORS extras, além das URLs locais padrão |
| `USE_FILENAME` | Não | `True` | Usa o nome original do arquivo no Cloudinary |
| `UNIQUE_FILENAME` | Não | `False` | Gera um sufixo único para o nome do arquivo |
| `OVERWRITE` | Não | `True` | Sobrescreve arquivo existente com o mesmo nome |
| `MEDIA_METADATA` | Não | `True` | Inclui metadados de mídia na resposta do Cloudinary |

Credenciais do Cloudinary são obtidas criando uma conta em [cloudinary.com](https://cloudinary.com/documentation/dev_kickstart_acct_setup).

---

## Rodando com Docker

### Docker CLI

```bash
# Build da imagem a partir do Dockerfile
docker build -t api-cloudinary .

# Execução usando um arquivo .env
docker run -d \
  --env-file .env \
  -p 8000:8000 \
  --name api-cloudinary \
  api-cloudinary
```

### Docker Compose

O `docker-compose.yml` do projeto já referencia o build local e o `.env`:

```yaml
services:
  api_cloudinary:
    build: .
    image: kevynsantos/cloudinary_api:V2.0
    container_name: cloudinary_Api_test
    ports:
      - "8000:8000"
    env_file:
      - .env
```

```bash
docker compose up -d
```

> Crie o `.env` na raiz do projeto (a partir de `sample.env`) antes de subir o container — a aplicação não inicia sem `CLOUD_NAME`, `API_KEY` e `API_SECRET`.

---

## Endpoint disponível

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/SendImage` | Envia uma ou mais imagens para o Cloudinary |

**Body** (`multipart/form-data`):

| Campo | Tipo | Descrição |
|---|---|---|
| `Image` | `file[]` | Uma ou mais imagens (máx. 5, até 100 MB no total) |
| `dirName` | `string` | Nome da pasta de destino no Cloudinary |

**Resposta de sucesso (`200`):**

```json
{
  "Link das imagens": [
    "https://res.cloudinary.com/seu-cloud/image/upload/..."
  ]
}
```

**Limite excedido (`429`):**

```json
{
  "status code": 429,
  "message": "Limite de envios atingido, tente novamente em alguns segundos"
}
```

---

## Testes

```bash
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

A suíte cobre testes unitários (models e serviços), testes de integração do endpoint e testes não-funcionais de rate limiting.
