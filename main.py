#Importação da bibioteca FASTAPI e suas dependencias
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates as j2t
from fastapi.responses import HTMLResponse

# Importação de arquivo com o código de upload do cloudinary
import Upload

# Bibliotecas para manipulação de arquivos de sistema
import shutil 
import os
import re

# Configuração
UPLOAD_FOLDER = 'uploaded_images'
LIMITE_IMAGENS = 5 # Limite de imagens que podem ser enviadas

app = FastAPI() # Cria a instancia do Fastapi
templates = j2t(directory= 'templates') # Indica onde esta a pagina HTML a ser renderizada
PaginaHTML = 'Images.html'
os.makedirs(UPLOAD_FOLDER, exist_ok = True) # Cria uma pasta para armazenar as imagens


# Renderiza a pagina HTML
@app.get("/", response_class=HTMLResponse) # Recebe ua resposta em HTML da pagina raiz
def renderizarPagina(request: Request):
    return templates.TemplateResponse(PaginaHTML, {'request': request}) # Recebe a requisição para renderizar com base no arquivo html

# Retorna dados da imagem e faz Upload no Cloudinary
@app.post('/enviar')
def detalhes_de_Imagem(Imagem: list[UploadFile] = File(...), Nome_Pasta: str = Form(...)):

    # Padronização de nomes de pastas
    Nome_Pasta = re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z\s]', '', Nome_Pasta)).lower().strip('_') # Remove caracteres especiais, números e espaços, deixando apenas letras minúsculas e underscores

    if len(Imagem) > LIMITE_IMAGENS: # Verifica se o número de imagens é maior que 5
        return {'status': 'erro', 'mensagem': 'Você pode enviar no máximo 5 imagens.'}
    else:

        # Cria uma lista com os nomes dos arquivos e seus caminhos
        NomeImagem =[nomes.filename for nomes in Imagem]
        caminhoImagem = [os.path.join(UPLOAD_FOLDER, nome) for nome in NomeImagem]
        Url_Imagem = []

        # Itera sobre cada imagem, salva em disco e faz o upload para o Cloudinary
        for imagem_item, caminho in zip(Imagem, caminhoImagem):
            with open(caminho, 'wb') as buffer:
                shutil.copyfileobj(imagem_item.file, buffer)
                
            caminho_absoluto = os.path.abspath(caminho)
            Url = Upload.uploadImagem(caminho_absoluto, Nome_Pasta)
            Url_Imagem.append(Url[0])
        
        # Retorna os principais dados da imagem e o link de upload
        return {
            'nomes das imagens': NomeImagem,
            'link das imagens': [link for link in Url_Imagem],
            'pasta salva': Url[1]
            }