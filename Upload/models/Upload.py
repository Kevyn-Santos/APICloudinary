# importação da biblioteca do cloudinary junto das suas dependencias principais
import cloudinary
import cloudinary.uploader

# Importação de bibliotecas adicionais para manipulação de arquivos em sistema
from Core.Settings import configs

#configurações principais do cloudinary a aprtir da variavel de ambiente
cloudinary.config(
    cloud_name = configs.CLOUD_NAME,
    api_key = configs.API_KEY,
    api_secret =  configs.API_SECRET,
    secure = True
)

# Principal função que executa o upload de arquivos para o cloudinary
def uploadImagem(caminho: str, Pasta: str):

    # Faz o upload utilizando os métodos próprios da biblioteca
    upload_result = cloudinary.uploader.upload( 
        caminho,
        use_filename = configs.USE_FILENAME,
        unique_filename= configs.UNIQUE_FILENAME,
        overwrite = configs.OVERWRITE,
        asset_folder = Pasta,
        media_metadata = configs.MEDIA_METADATA,
        )
     
    URL = upload_result['secure_url']
    return URL