#Importação da bibioteca FASTAPI e suas dependencias
from fastapi import FastAPI, APIRouter,UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

# Importação de arquivo com o código de upload do cloudinary
from Services.Upload import uploadImagem
from Upload.models.imageModels import Imagem
from Core.Settings import configs

# Bibliotecas para manipulação de arquivos de sistema
import shutil 
import os
import re


app = FastAPI(
    title=configs.PROJECT_NAME,
    description=configs.DESCRIPTION
) # Cria a instancia do Fastapi

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

os.makedirs(configs.UPLOAD_FOLDER, exist_ok = True) # Cria uma pasta para armazenar as imagens


# Retorna dados da imagem e faz Upload no Cloudinary
@app.post('/enviar')
def detalhes_de_Imagem(Imagem: list[UploadFile] = File(...), Nome_Pasta: str = Form(...)):

    # Padronização de nomes de pastas
    Nome_Pasta = re.sub(r'\s+', '_', re.sub(r'\d+', '', Nome_Pasta)).lower().strip('_') # Remove caracteres especiais, números e espaços, deixando apenas letras minúsculas e underscores

    if len(Imagem) > configs.LIMITE_IMAGENS: # Verifica se o número de imagens é maior que 5
        return {'status': 'erro', 'mensagem': 'Você pode enviar no máximo 5 imagens.'}
    else:

        # Cria uma lista com os nomes dos arquivos e seus caminhos
        NomeImagem =[nomes.filename for nomes in Imagem if nomes.filename]
        caminhoImagem = [os.path.join(configs.UPLOAD_FOLDER, nome) for nome in NomeImagem]
        Url_Imagem = []

        # Itera sobre cada imagem, salva em disco e faz o upload para o Cloudinary
        for imagem_item, caminho in zip(Imagem, caminhoImagem):
            with open(caminho, 'wb') as buffer:
                shutil.copyfileobj(imagem_item.file, buffer)
                
            caminho_absoluto = os.path.abspath(caminho)
            
            Url = uploadImagem(caminho_absoluto, Nome_Pasta)
            Url_Imagem.append(Url)
            
        # Retorna os principais dados da imagem e o link de upload
        return {
            'link das imagens': [link for link in Url_Imagem],
            }