from fastapi import APIRouter
from controllers import logro_controller
from schemas.logro_schema import LogroBase

router = APIRouter()

@router.get("/logros/{logro_id}", response_model=LogroBase)
def get_logro(logro_id: str):
    """
    Obtiene un logro por su ID.
    """
    return logro_controller.get_logro_by_id(logro_id)


@router.get("/logros", response_model=list[LogroBase])
def get_all_logros():
    """
    Obtiene todos los logros.
    """
    return logro_controller.get_all_logros()


@router.post("/logros", response_model=str)
def create_logro(logro_data: LogroBase):
    """
    Crea un nuevo logro.
    """
    return logro_controller.create_logro(logro_data.dict())


@router.put("/logros/{logro_id}", response_model=str)
def update_logro(logro_id: str, logro_data: LogroBase):
    """
    Actualiza un logro existente.
    """
    return logro_controller.update_logro(logro_id, logro_data.dict())


@router.delete("/logros/{logro_id}", response_model=str)
def delete_logro(logro_id: str):
    """
    Elimina un logro por su ID.
    """
    return logro_controller.delete_logro(logro_id)


@router.get("/logros/usuario/{usuario_id}", response_model=list[LogroBase])
def get_logros_by_usuario(usuario_id: str):
    """
    Obtiene todos los logros asociados a un usuario.
    """
    return logro_controller.get_logros_by_usuario(usuario_id)

@router.post("/usuarios/{usuario_id}/agregar/{logro_id}")
async def agregar_logro_a_usuario(usuario_id: str, logro_id: str):
    """
    Agrega un logro a un usuario.
    """
    return logro_controller.add_logro_to_usuario(usuario_id, logro_id)


@router.get("/usuarios/{usuario_id}/tipo/{tipo}")
async def obtener_logros_por_tipo(usuario_id: str, tipo: str):
    """
    Obtiene los logros de un usuario por tipo.
    """
    return logro_controller.get_logros_tipo(usuario_id, tipo)