from fastapi import APIRouter
from controllers import usuario_controller

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/")
async def crear_usuario(data: dict):
    return await usuario_controller.crear_usuario(data)

@router.get("/")
async def listar_usuarios():
    return await usuario_controller.obtener_usuarios()
