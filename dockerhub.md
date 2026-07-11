# API CLOUDINARY

API REST em FastAPI que recebe imagens via `multipart/form-data` e as envia diretamente para o Cloudinary — sem salvar em disco —, retornando as `secure_url`s dos arquivos enviados.

## Versões disponíveis

A imagem é publicada em [`kevynsantos/cloudinary_api`](https://hub.docker.com/r/kevynsantos/cloudinary_api) seguindo versionamento semântico (`major.minor`), por exemplo `V1.0`, `V2.0`, etc.

| Tag | Descrição |
|---|---|
| `latest` | Sempre aponta para a versão estável mais recente |
| `V2.0` | Versão estável atual — a mesma referenciada no `docker-compose.yml` do repositório |
| `V1.0`, ... | Versões anteriores, mantidas para compatibilidade |

A tag numerada mais alta e a tag `latest` apontam para a mesma imagem — use `latest` se quiser sempre a versão mais recente, ou fixe uma tag numerada (ex: `V2.0`) se precisar de reprodutibilidade.

## Instanciando a imagem

### Docker CLI

```bash
docker run --env-file .env -p 8000:8000 kevynsantos/cloudinary_api:V2.0
```

### Docker Compose

```yaml
services:
  api_cloudinary:
    image: kevynsantos/cloudinary_api:V2.0
    container_name: cloudinary_api
    ports:
      - "8000:8000"
    env_file:
      - .env
```

```bash
docker compose up
```

## Requisitos do front

*Endpoint:* `POST /SendImage`

*Inputs:*

`type="text" name="dirName"` — nome da pasta/diretório no Cloudinary onde as imagens serão salvas

`type="file" name="Image" accept=".png,.jpg,.jpeg" multiple` — lista de imagens (máximo de 5 por envio, 100 MB no total)

```js
// Exemplo de fetch que captura o retorno e o exibe em um blob/JSON
const form = document.getElementById('upload-form');
const submitBtn = document.getElementById('submit-btn');
const statusMsg = document.getElementById('status-msg');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  statusMsg.className = 'loading';
  statusMsg.textContent = 'Enviando…';
  submitBtn.disabled = true;

  const formData = new FormData(form);

  try {
    const response = await fetch('http://0.0.0.0:8000/SendImage', {
      method: 'POST',
      body: formData,
    });

    console.log(response.status);

    if (response.ok) {
      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const objectURL = URL.createObjectURL(blob);
      window.location.href = objectURL;
    } else {
      const errorText = await response.text();
      statusMsg.className = 'error';
      statusMsg.textContent = `Erro no envio: ${response.status} — ${errorText}`;
      submitBtn.disabled = false;
    }
  } catch (err) {
    console.log('Erro de rede:', err);
    statusMsg.className = 'error';
    statusMsg.textContent = 'Falha na conexão com o servidor. Verifique se a API está rodando.';
    submitBtn.disabled = false;
  }
});
```

A resposta de sucesso tem o formato `{"Link das imagens": ["https://...", ...]}`.

## Variáveis de ambiente

### Obrigatórias

Sem estas, a aplicação não sobe. São obtidas criando uma conta gratuita em [cloudinary.com](https://cloudinary.com/documentation/dev_kickstart_acct_setup):

`CLOUD_NAME` - Nome da cloud criada na conta do Cloudinary

`API_KEY` - Chave de API da conta do Cloudinary

`API_SECRET` - Secret da API da conta do Cloudinary

### Opcionais

`LIMITE_IMAGENS` (padrão `5`) - Número máximo de requisições permitidas por IP dentro da janela de tempo definida em `LIMITE_TEMPO`

`LIMITE_TEMPO` (padrão `10`) - Janela de tempo, em segundos, usada pelo rate limiter junto com `LIMITE_IMAGENS`

`HOSTS` (padrão vazio) - Origens extras liberadas no CORS, além dos endereços locais padrão (registre como lista separada por vírgulas e sem espaços, ex: `https://meusite.com,https://outrosite.com`)

### Personalização (Cloudinary)

`USE_FILENAME` (padrão `True`) - Usa o nome original do arquivo como parte do `public_id` gerado no Cloudinary

`UNIQUE_FILENAME` (padrão `False`) - Adiciona um sufixo aleatório ao nome do arquivo para evitar colisões

`OVERWRITE` (padrão `True`) - Sobrescreve um arquivo existente com o mesmo `public_id`

## Exemplo de docker-compose.yml com variáveis inline

Configuração de exemplo com valores fictícios, para ilustrar um uso real da imagem publicada:

```yaml
services:
  api_cloudinary:
    image: kevynsantos/cloudinary_api:V2.0
    container_name: cloudinary_api
    ports:
      - "8000:8000"
    environment:
      CLOUD_NAME: minha-loja-fotos
      API_KEY: "123456789012345"
      API_SECRET: aB3dEfGhIjKlMnOpQrStUvWxYz12
      LIMITE_IMAGENS: 8
      LIMITE_TEMPO: 30
      HOSTS: https://minhaloja.com.br,https://admin.minhaloja.com.br
      USE_FILENAME: "True"
      UNIQUE_FILENAME: "False"
      OVERWRITE: "True"
      MEDIA_METADATA: "True"
```

> Os valores acima (`CLOUD_NAME`, `API_KEY`, `API_SECRET`, `HOSTS`) são fictícios — substitua pelas credenciais reais da sua conta Cloudinary e pelas origens do seu próprio front-end.
