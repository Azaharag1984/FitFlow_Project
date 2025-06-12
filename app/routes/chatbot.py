from fastapi import APIRouter, Path, Query
from controllers import conversacion_controller
from schemas.conversacion_schema import ConversacionesSchema

router = APIRouter()

@router.get("/conversaciones/{conversacion_id}", response_model=ConversacionesSchema)
def get_conversacion(conversacion_id: str):
    """
    Obtiene una conversación por su ID.
    """
    return conversacion_controller.get_conversacion_by_id(conversacion_id)


@router.get("/conversaciones", response_model=list[ConversacionesSchema])
def get_all_conversaciones():
    """
    Obtiene todas las conversaciones.
    """
    return conversacion_controller.get_all_conversaciones()


@router.post("/conversaciones", response_model=str)
def create_conversacion(conversacion_data: ConversacionesSchema):
    """
    Crea una nueva conversación.
    """
    return conversacion_controller.create_conversacion(conversacion_data.dict())


@router.put("/conversaciones/{conversacion_id}", response_model=str)
def update_conversacion(conversacion_id: str, conversacion_data: ConversacionesSchema):
    """
    Actualiza una conversación existente.
    """
    return conversacion_controller.update_conversacion(conversacion_id, conversacion_data.dict())


@router.delete("/conversaciones/{conversacion_id}", response_model=str)
def delete_conversacion(conversacion_id: str):
    """
    Elimina una conversación por su ID.
    """
    return conversacion_controller.delete_conversacion(conversacion_id)


@router.get("/conversaciones/usuario/{usuario_id}", response_model=list[ConversacionesSchema])
def get_conversaciones_by_usuario(usuario_id: str):
    """
    Obtiene todas las conversaciones asociadas a un usuario.
    """
    return conversacion_controller.get_conversaciones_by_usuario(usuario_id)


@router.get("/usuarios/{usuario_id}/ultimos-mensajes")
async def obtener_ultimos_mensajes(
usuario_id: str = Path(..., description="ID del usuario"),
n: int = Query(5, description="Número de mensajes a recuperar")
):
    """
    Obtiene los últimos mensajes de un usuario.
    """
    return conversacion_controller.get_ultimos_mensajes(usuario_id, n)


@router.get("/usuarios/{usuario_id}/mensajes/tema")
async def obtener_mensajes_por_tema(
usuario_id: str = Path(..., description="ID del usuario"),
tema: str = Query(..., description="Tema de los mensajes")
):
    """
    Obtiene los mensajes de un usuario por tema.
    """
    return conversacion_controller.get_mensajes_por_tema(usuario_id, tema)


@router.get("/usuarios/{usuario_id}/estado-animo")
async def obtener_estado_animo(
usuario_id: str = Path(..., description="ID del usuario")
):
    """
    Analiza el estado de ánimo de un usuario basado en sus conversaciones.
    """
    from controllers import conversaciones_controller
    return conversacion_controller.analizar_estado_animo(usuario_id)