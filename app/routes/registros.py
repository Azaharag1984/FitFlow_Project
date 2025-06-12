from fastapi import APIRouter
from controllers import registro_controller
from schemas.registro_schema import RegistrosSchema

router = APIRouter()

@router.get("/registros/{registro_id}", response_model=RegistrosSchema)
def get_registro(registro_id: str):
    """
    Obtiene un registro por su ID.
    """
    return registro_controller.get_registro_by_id(registro_id)


@router.get("/registros", response_model=list[RegistrosSchema])
def get_all_registros():
    """
    Obtiene todos los registros.
    """
    return registro_controller.get_all_registros()


@router.post("/registros", response_model=str)
def create_registro(registro_data: RegistrosSchema):
    """
    Crea un nuevo registro.
    """
    return registro_controller.create_registro(registro_data.dict())


@router.put("/registros/{registro_id}", response_model=str)
def update_registro(registro_id: str, registro_data: RegistrosSchema):
    """
    Actualiza un registro existente.
    """
    return registro_controller.update_registro(registro_id, registro_data.dict())


@router.delete("/registros/{registro_id}", response_model=str)
def delete_registro(registro_id: str):
    """
    Elimina un registro por su ID.
    """
    return registro_controller.delete_registro(registro_id)


@router.get("/registros/usuario/{usuario_id}", response_model=list[RegistrosSchema])
def get_registros_by_usuario(usuario_id: str):
    """
    Obtiene todos los registros asociados a un usuario.
    """
    return registro_controller.get_registros_by_usuario(usuario_id)


@router.get("/registros/{usuario_id}/{ejercicio_nombre}", tags=["Registros"])
async def obtener_historial_por_ejercicio(usuario_id: str, ejercicio_nombre: str):
    """
    Obtiene el historial de un ejercicio específico para un usuario.
    """
    return await registro_controller.get_historial_por_ejercicio(usuario_id, ejercicio_nombre)


@router.get("/usuarios/{usuario_id}/registros/por-fecha/{fecha_inicio}/{fecha_fin}", tags=["Registros"])
async def obtener_registros_por_fecha(
usuario_id: str,
fecha_inicio: str,
fecha_fin: str
):
    """
    Obtiene los registros de un usuario en un rango de fechas específico.
    """
    return await registro_controller.get_registros_por_fecha(usuario_id, fecha_inicio, fecha_fin)