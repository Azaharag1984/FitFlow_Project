from fastapi import APIRouter
from controllers import conversacion_controller
from schemas.usuario_schema import UsuariosSchema

router = APIRouter()

@router.get("/usuarios/{usuario_id}", response_model=UsuariosSchema)
def get_usuario(usuario_id: str):
    """
    Obtiene un usuario por su ID.
    """
    return conversacion_controller.get_usuario_by_id(usuario_id)


@router.get("/usuarios", response_model=list[UsuariosSchema])
def get_all_usuarios():
    """
    Obtiene todos los usuarios.
    """
    return conversacion_controller.get_all_usuarios()


@router.post("/usuarios", response_model=str)
def create_usuario(usuario_data: UsuariosSchema):
    """
    Crea un nuevo usuario.
    """
    return conversacion_controller.create_usuario(usuario_data.dict())


@router.put("/usuarios/{usuario_id}", response_model=str)
def update_usuario(usuario_id: str, usuario_data: UsuariosSchema):
    """
    Actualiza un usuario existente.
    """
    return conversacion_controller.update_usuario(usuario_id, usuario_data.dict())


@router.delete("/usuarios/{usuario_id}", response_model=str)
def delete_usuario(usuario_id: str):
    """
    Elimina un usuario por su ID.
    """
    return conversacion_controller.delete_usuario(usuario_id)

