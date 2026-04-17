# APICloudinary

API HTTP leve, construída em **FastAPI**, que recebe imagens via upload multipart e as publica no **Cloudinary**, devolvendo as URLs seguras geradas. Foi projetada para ser um microsserviço de *asset ingestion* — o cliente (frontend, app ou outro backend) envia um lote de imagens junto com o nome de uma pasta lógica, e a API se encarrega de normalizar o nome, persistir os arquivos temporariamente em disco e delegar o armazenamento definitivo ao Cloudinary.

O deploy-alvo é a **Vercel** (runtime Python 3.12), o que torna a API efêmera e *stateless*: nenhum arquivo é mantido no servidor após o upload.

---

## Como funciona em alto nível

```
┌──────────┐   multipart/form-data    ┌─────────────────┐    SDK    ┌──────────────┐
│  Cliente │ ───────────────────────▶ │  FastAPI (/env) │ ────────▶ │  Cloudinary  │
└──────────┘   Imagem[], Nome_Pasta   └─────────────────┘           └──────────────┘
                                              │                             │
                                              ▼                             │
                                       /tmp (buffer)                        │
                                              ▲                             │
                                              └──── secure_url ◀────────────┘
```

1. O cliente envia um `POST /enviar` com um ou mais arquivos no campo `Imagem` e um nome de pasta no campo `Nome_Pasta`.
2. A API normaliza o nome da pasta (remove números, caracteres especiais e espaços; força minúsculas).
3. Cada arquivo é salvo no diretório temporário `/tmp`.
4. Cada arquivo é então enviado para o Cloudinary, dentro do `asset_folder` normalizado.
5. A API devolve um JSON contendo a lista de URLs públicas (`secure_url`) dos assets criados.

---

## Tecnologias principais

| Camada | Tecnologia | Papel |
|---|---|---|
| Web framework | **FastAPI** `0.116.1` | Define as rotas, parsing de `multipart/form-data`, geração automática de OpenAPI/Swagger |
| Servidor ASGI | **Uvicorn** `0.35.0` | Execução local do app FastAPI |
| Armazenamento de mídia | **Cloudinary SDK** `1.44.1` | Upload, organização em *asset folders* e entrega por CDN |
| Validação | **Pydantic** `2.11.7` | Modelos de dados e validação tipada |
| Configuração | **python-dotenv** `0.9.9` | Carregamento de credenciais Cloudinary via `.env` |
| Upload multipart | **python-multipart** `0.0.20` | Suporte de `UploadFile` no FastAPI |
| Deploy | **Vercel** (`@vercel/python`, Python 3.12.6) | Hospedagem serverless |

---

## Estrutura do projeto

### Estado atual

```
APICloudinary/
├── UploadCode/
│   ├── main.py          # App FastAPI + rota /enviar + orquestração
│   └── Upload.py        # Configuração do Cloudinary + função uploadImagem
├── requirements.txt     # Dependências Python
├── vercel.json          # Config de build/rota para a Vercel
└── .gitignore
```

Hoje o projeto é compacto: dois arquivos concentram responsabilidades de HTTP, I/O em disco, sanitização de strings e integração com o Cloudinary. Funciona bem para o caso de uso atual, mas tende a dificultar evolução e testes à medida que novas regras aparecerem.

### Direção: monolito modular

A evolução planejada do projeto segue o padrão **monolito modular** — um único artefato deployável (preservando o ponto de entrada esperado pela Vercel), mas internamente segmentado por responsabilidade:

```
UploadCode/
├── main.py                          # app factory; registra middleware e routers
├── config/
│   └── settings.py                  # carrega/valida variáveis de ambiente
├── core/
│   ├── exceptions.py                # exceções tipadas + handlers
│   └── logging.py                   # logger centralizado
├── modules/
│   └── upload/
│       ├── router.py                # POST /enviar
│       ├── schemas.py               # contratos Pydantic
│       ├── service.py               # orquestração do pipeline
│       ├── sanitizer.py             # normalização do nome da pasta
│       ├── validators.py            # regras de quantidade/tamanho/extensão
│       ├── storage.py               # salvar/limpar arquivos em disco
│       └── cloudinary_client.py     # configuração e função de upload
└── tests/
```

A ideia central é que cada módulo tenha **uma única razão para mudar**: trocar o provedor de storage, ajustar o pipeline de upload, mudar regras de validação ou a forma de logging devem ser alterações locais, independentes entre si. Configuração fica fora do código, em variáveis de ambiente com defaults seguros.

---

## Rotas

### `POST /enviar`

Recebe um lote de imagens e publica cada uma no Cloudinary.

**Content-Type:** `multipart/form-data`

**Campos:**

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `Imagem` | `File` (múltiplos) | sim | Um ou mais arquivos de imagem. Máximo **5** por requisição. |
| `Nome_Pasta` | `string` | sim | Nome lógico da pasta no Cloudinary. Será normalizado. |

**Ordem de execução interna:**

1. **Recepção** — FastAPI faz o *parsing* do `multipart` e popula `Imagem: list[UploadFile]` e `Nome_Pasta: str`.
2. **Normalização do nome da pasta** — remove dígitos, troca espaços por `_`, força minúsculas e tira `_` das pontas.
   Ex.: `"Fotos 2024 Cliente!"` → `fotos_cliente`.
3. **Validação de quantidade** — se `len(Imagem) > 5`, a API retorna imediatamente `{"status": "erro", "mensagem": "Você pode enviar no máximo 5 imagens."}` e **não faz upload**.
4. **Montagem de caminhos** — para cada arquivo, constrói o caminho destino em `/tmp/<filename>`.
5. **Persistência temporária** — cada arquivo é escrito em `/tmp` usando `shutil.copyfileobj`.
6. **Upload no Cloudinary** — para cada caminho absoluto, `Upload.uploadImagem(caminho, Nome_Pasta)` é invocado. Essa função:
   - Usa as credenciais lidas de `CLOUD_NAME`, `API_KEY`, `API_SECRET` (via `dotenv`).
   - Envia com `use_filename=True`, `unique_filename=False`, `overwrite=True`, `asset_folder=<Nome_Pasta>`, `media_metadata=True`.
   - Retorna `upload_result["secure_url"]`.
7. **Agregação da resposta** — as URLs são acumuladas e devolvidas ao cliente.

**Resposta (200):**
```json
{
  "link das imagens": [
    "https://res.cloudinary.com/<cloud>/image/upload/v.../fotos_cliente/foo.jpg",
    "https://res.cloudinary.com/<cloud>/image/upload/v.../fotos_cliente/bar.png"
  ]
}
```

**Resposta (limite excedido):**
```json
{ "status": "erro", "mensagem": "Você pode enviar no máximo 5 imagens." }
```

**Exemplo (`curl`):**
```bash
curl -X POST https://<seu-deploy>/enviar \
  -F "Imagem=@foto1.jpg" \
  -F "Imagem=@foto2.png" \
  -F "Nome_Pasta=Portfolio 2024"
```

### Documentação interativa

Com a aplicação em execução, o Swagger UI fica disponível em `/docs` e o ReDoc em `/redoc` (gerados automaticamente pelo FastAPI).

---

## Configuração

Variáveis de ambiente exigidas (via `.env` em desenvolvimento ou *Environment Variables* na Vercel em produção):

| Variável | Descrição |
|---|---|
| `CLOUD_NAME` | Nome da sua conta Cloudinary |
| `API_KEY` | Chave de API do Cloudinary |
| `API_SECRET` | Segredo de API do Cloudinary |

> O `.env` está no `.gitignore` e **não deve ser commitado**.

### Execução local

```bash
pip install -r requirements.txt
uvicorn UploadCode.main:app --reload
```

A API ficará disponível em `http://localhost:8000`.

---

## Casos de uso

- **Upload em lote a partir de formulários web** — o frontend coleta várias imagens (ex.: fotos de um imóvel, itens de um portfólio) e envia tudo em uma única requisição.
- **Organização por cliente/campanha** — `Nome_Pasta` permite agrupar assets logicamente no Cloudinary sem que o cliente precise conhecer a API do Cloudinary.
- **Backend intermediário** — esconde as credenciais do Cloudinary do cliente: só o servidor conhece `API_KEY` e `API_SECRET`.
- **Pré-processamento centralizado** — ponto único onde futuras regras (compressão, watermark, validação de MIME, moderação) podem ser adicionadas sem alterar o cliente.

---

## Limitações atuais

- **Máximo de 5 imagens por requisição.** Lotes maiores retornam erro sem processar nada.
- **Sem limite explícito de tamanho por arquivo** na aplicação. Na Vercel, o tamanho do corpo da requisição é limitado pela própria plataforma (tipicamente alguns MB em funções serverless), o que pode rejeitar uploads grandes antes mesmo de chegar ao código.
- **Sem filtro de extensão/MIME type** — qualquer arquivo enviado como `Imagem` é encaminhado ao Cloudinary, que fará a própria validação.
- **Armazenamento local efêmero** — `/tmp` é volátil na Vercel; os arquivos salvos ali somem ao final da execução (e isso é intencional), mas não há limpeza explícita no código após o upload.
- **Concorrência** — os uploads são feitos **sequencialmente** dentro de uma requisição (loop `for`), não em paralelo.
- **CORS aberto** — `allow_origins=["*"]` está ativo; adequado para testes, mas deve ser restrito em produção.
- **Tratamento de erros limitado** — falhas no Cloudinary (credenciais inválidas, indisponibilidade, etc.) não são capturadas explicitamente e podem retornar `500` genérico.
- **Sem autenticação** — qualquer cliente com acesso à URL consegue enviar imagens. Recomendado colocar atrás de um gateway/token antes de expor publicamente.
- **Resposta reduzida** — apenas `secure_url` é devolvido; metadados do Cloudinary (`public_id`, `bytes`, `format`, `width`, `height`) são descartados.

Parte dessas limitações é tratada pela proposta de modularização descrita na seção de estrutura: limite de tamanho/extensão por variável de ambiente, limpeza de arquivos temporários, exceções tipadas com respostas consistentes e resposta enriquecida com metadados.

---

## Deploy

O deploy na Vercel é declarado em `vercel.json`, com `UploadCode/main.py` como entry point e todas as rotas (`/(.*)`) roteadas para esse módulo. Basta configurar as três variáveis de ambiente do Cloudinary no painel da Vercel e conectar o repositório.
