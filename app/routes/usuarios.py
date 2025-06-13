from fastapi import APIRouter
from controllers import usuario_controller
from schemas.usuario_schema import UsuariosSchema


router = APIRouter()

@router.get("/usuarios/{usuario_id}", response_model=UsuariosSchema)
def get_usuario(usuario_id: str):
    """
    Obtiene un usuario por su ID.
    """
    return usuario_controller.get_usuario_by_id(usuario_id)


@router.get("/usuarios", response_model=list[UsuariosSchema])
def get_all_usuarios():
    """
    Obtiene todos los usuarios.
    """
    return usuario_controller.get_all_usuarios()


@router.post("/usuarios", response_model=str)
def create_usuario(usuario_data: UsuariosSchema):
    """
    Crea un nuevo usuario.
    """
    return usuario_controller.create_usuario(usuario_data.dict())


@router.put("/usuarios/{usuario_id}", response_model=str)
def update_usuario(usuario_id: str, usuario_data: UsuariosSchema):
    """
    Actualiza un usuario existente.
    """
    return usuario_controller.update_usuario(usuario_id, usuario_data.dict())


@router.delete("/usuarios/{usuario_id}", response_model=str)
def delete_usuario(usuario_id: str):
    """
    Elimina un usuario por su ID.
    """
    return usuario_controller.delete_usuario(usuario_id)


@router.get("/usuarios/{usuario_id}/progreso", tags=["Progreso"])
async def obtener_ultimo_peso_por_ejercicio(usuario_id: str):
    """
    Obtiene el último peso registrado por ejercicio para un usuario.
    """
    return await usuario_controller.get_ultimo_peso_por_ejercicio(usuario_id)


@router.get("/usuarios/{usuario_id}/progreso/{ejercicio_nombre}/mejor_marca", tags=["Progreso"])
async def obtener_mejor_marca(usuario_id: str, ejercicio_nombre: str):
    """
    Obtiene la mejor marca de un ejercicio específico para un usuario.
    """
    return await usuario_controller.get_mejor_marca(usuario_id, ejercicio_nombre)


@router.get("/usuarios/{usuario_id}/progreso/frecuencia_semanal", tags=["Progreso"])
async def obtener_frecuencia_semanal(usuario_id: str):
    """
    Obtiene la frecuencia semanal de registros de un usuario.
    """
    return await usuario_controller.get_frecuencia_semanal(usuario_id)


@router.get("/usuarios/{usuario_id}/progreso/volumen_total", tags=["Progreso"])
async def obtener_volumen_total(usuario_id: str):
    """
    Obtiene el volumen total de levantamiento de un usuario.
    """
    return await usuario_controller.get_volumen_total(usuario_id)


