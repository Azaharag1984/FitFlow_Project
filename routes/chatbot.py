from fastapi import APIRouter
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
