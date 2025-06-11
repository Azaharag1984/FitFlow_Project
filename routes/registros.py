from fastapi import APIRouter
from controllers import conversacion_controller
from schemas.registro_schema import RegistrosSchema

router = APIRouter()

@router.get("/registros/{registro_id}", response_model=RegistrosSchema)
def get_registro(registro_id: str):
    """
    Obtiene un registro por su ID.
    """
    return conversacion_controller.get_registro_by_id(registro_id)


@router.get("/registros", response_model=list[RegistrosSchema])
def get_all_registros():
    """
    Obtiene todos los registros.
    """
    return conversacion_controller.get_all_registros()


@router.post("/registros", response_model=str)
def create_registro(registro_data: RegistrosSchema):
    """
    Crea un nuevo registro.
    """
    return conversacion_controller.create_registro(registro_data.dict())


@router.put("/registros/{registro_id}", response_model=str)
def update_registro(registro_id: str, registro_data: RegistrosSchema):
    """
    Actualiza un registro existente.
    """
    return conversacion_controller.update_registro(registro_id, registro_data.dict())


@router.delete("/registros/{registro_id}", response_model=str)
def delete_registro(registro_id: str):
    """
    Elimina un registro por su ID.
    """
    return conversacion_controller.delete_registro(registro_id)


@router.get("/registros/usuario/{usuario_id}", response_model=list[RegistrosSchema])  
def get_registros_by_usuario(usuario_id: str):
    """
    Obtiene todos los registros asociados a un usuario.
    """
    return conversacion_controller.get_registros_by_usuario(usuario_id)
