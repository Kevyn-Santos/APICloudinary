# APICloudinary

Uma API REST leve e flexível para envio de imagens ao [Cloudinary](https://cloudinary.com/), projetada para ser facilmente integrada a qualquer projeto que precise de upload de mídia para a nuvem sem acoplamento à lógica de negócio da aplicação consumidora.

O usuário define suas próprias credenciais e preferências via variáveis de ambiente, tornando a ferramenta reutilizável em diferentes contas e contextos.

---

## Arquitetura

O projeto segue uma estrutura modular em camadas, onde cada diretório tem uma responsabilidade bem definida e o acoplamento entre elas é mínimo, o que facilita a expansão futura (novos provedores de storage, novos endpoints, novas regras de validação, etc.).

```
APICloudinary/
├── main.py               # Ponto de entrada: instância FastAPI, middlewares, roteamento
├── requirements.txt
├── Dockerfile
└── src/
    ├── Core/             # Infraestrutura transversal
    │   ├── Settings.py   # Carregamento de configurações via variáveis de ambiente
    │   └── security.py   # Rate limiting (slowapi)
    ├── Routes/           # Camada HTTP — define os endpoints e suas dependências
    │   └── Send.py
    ├── Services/         # Lógica de negócio — validação e integração com Cloudinary
    │   └── Upload.py
    └── models/           # Contratos de dados (Pydantic)
        └── imageModels.py
```

**Fluxo de dependências:** `Routes → Services → models + Core`

A camada `Core` é a única com acesso global; as demais só se comunicam para baixo na hierarquia.

---

## Principais bibliotecas e módulos

| Biblioteca | Função no projeto |
|---|---|
| **FastAPI** | Framework web — roteamento, validação de requisições, serialização de respostas |
| **Uvicorn** | Servidor ASGI que executa a aplicação |
| **Pydantic / pydantic-settings** | Validação de modelos de dados e carregamento tipado de variáveis de ambiente |
| **cloudinary** | SDK oficial para upload e gerenciamento de arquivos no Cloudinary |
| **slowapi** | Middleware de rate limiting baseado em IP, integrado ao FastAPI |
| **python-multipart** | Suporte ao recebimento de arquivos via `multipart/form-data` |
| **python-dotenv** | Carregamento de arquivos `.env` no ambiente de desenvolvimento |

---

## Ordem de execução

Em alto nível, uma requisição percorre o seguinte caminho:

```
1. Cliente envia POST /SendImage
   └─ multipart/form-data: { Image: [arquivo(s)], dirName: "nome-da-pasta" }

2. Rate Limiter (slowapi)
   └─ Verifica o limite de requisições por IP
   └─ HTTP 429 se excedido

3. Route handler (Routes/Send.py)
   └─ Recebe e monta o objeto Imagem (model)

4. parse_images (Services/Upload.py)
   ├─ Valida quantidade de arquivos (máx. configurável)
   ├─ Valida tamanho total (máx. 100 MB)
   ├─ Filtra arquivos inválidos
   └─ Sanitiza o nome da pasta (remove caracteres especiais, lowercase)

5. uploadImage (Services/Upload.py)  [executado para cada arquivo]
   └─ Envia o arquivo ao Cloudinary via SDK
   └─ Retorna a URL segura (HTTPS) do arquivo hospedado

6. Resposta ao cliente
   └─ JSON: { "Link das imagens": ["https://...", ...] }
```

---

## Configuração

Todas as configurações da aplicação — credenciais do Cloudinary, limites de rate, origens CORS permitidas e comportamento de upload — são definidas exclusivamente via **variáveis de ambiente** (ou arquivo `.env`).

Nenhum valor sensível é hardcoded. Consulte `src/Core/Settings.py` para ver todas as variáveis disponíveis e seus valores padrão.

---

## Exemplos de uso com Docker

### Dockerfile (já incluso no projeto)

O `Dockerfile` usa um build multi-stage com Python 3.12-Alpine para manter a imagem final enxuta. A aplicação roda como usuário não-root (`cloudinaryusr`) na porta `8000`.

Para construir e executar manualmente:

```bash
# Build da imagem
docker build -t apicloudinary .

# Execução passando as variáveis de ambiente diretamente
docker run -d \
  -p 8000:8000 \
  -e CLOUD_NAME=seu_cloud_name \
  -e API_KEY=sua_api_key \
  -e API_SECRET=seu_api_secret \
  --name apicloudinary \
  apicloudinary
```

---

### Docker Compose

```yaml
services:
  apicloudinary:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
```

```bash
docker compose up -d
```

> As variáveis de ambiente são lidas do arquivo `.env` na raiz do projeto.

---

### Docker CLI com imagem publicada

Caso a imagem esteja publicada em um registry (ex.: Docker Hub):

```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name apicloudinary \
  seu-usuario/apicloudinary:latest
```

---

## Endpoint disponível

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/SendImage` | Envia uma ou mais imagens para o Cloudinary |

**Body** (`multipart/form-data`):

| Campo | Tipo | Descrição |
|---|---|---|
| `Image` | `file[]` | Um ou mais arquivos de imagem |
| `dirName` | `string` | Nome da pasta de destino no Cloudinary |

**Resposta de sucesso (`200`):**

```json
{
  "Link das imagens": [
    "https://res.cloudinary.com/seu-cloud/image/upload/..."
  ]
}
```

---

## Testes

```bash
pip install -r requirements.txt
pytest
```

A suíte cobre testes unitários (models e serviços), testes de integração do endpoint e testes não-funcionais de rate limiting.
