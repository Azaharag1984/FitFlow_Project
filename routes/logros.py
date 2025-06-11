from fastapi import APIRouter
from controllers import conversacion_controller
from schemas.logro_schema import LogrosSchema

router = APIRouter()

@router.get("/logros/{logro_id}", response_model=LogrosSchema)
def get_logro(logro_id: str):
    """
    Obtiene un logro por su ID.
    """
    return conversacion_controller.get_logro_by_id(logro_id)


@router.get("/logros", response_model=list[LogrosSchema])
def get_all_logros():
    """
    Obtiene todos los logros.
    """
    return conversacion_controller.get_all_logros()


@router.post("/logros", response_model=str)
def create_logro(logro_data: LogrosSchema):
    """
    Crea un nuevo logro.
    """
    return conversacion_controller.create_logro(logro_data.dict())


@router.put("/logros/{logro_id}", response_model=str)
def update_logro(logro_id: str, logro_data: LogrosSchema):
    """
    Actualiza un logro existente.
    """
    return conversacion_controller.update_logro(logro_id, logro_data.dict())


@router.delete("/logros/{logro_id}", response_model=str)
def delete_logro(logro_id: str):
    """
    Elimina un logro por su ID.
    """
    return conversacion_controller.delete_logro(logro_id)


@router.get("/logros/usuario/{usuario_id}", response_model=list[LogrosSchema])
def get_logros_by_usuario(usuario_id: str):
    """
    Obtiene todos los logros asociados a un usuario.
    """
    return conversacion_controller.get_logros_by_usuario(usuario_id)