from fastapi import APIRouter

router = APIRouter(prefix='/enviar', tags=['SendImages'])

@router.post('/enviar')
def parse_image():
    
    pass