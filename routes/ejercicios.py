from fastapi import APIRouter
from controllers import conversacion_controller
from schemas.ejercicio_schema import EjerciciosSchema

router = APIRouter()


@router.get("/ejercicios/{ejercicio_id}", response_model=EjerciciosSchema)
def get_ejercicio(ejercicio_id: str):
    """
    Obtiene un ejercicio por su ID.
    """
    return conversacion_controller.get_ejercicio_by_id(ejercicio_id)


@router.get("/ejercicios", response_model=list[EjerciciosSchema])
def get_all_ejercicios():
    """
    Obtiene todos los ejercicios.
    """
    return conversacion_controller.get_all_ejercicios()


@router.post("/ejercicios", response_model=str)
def create_ejercicio(ejercicio_data: EjerciciosSchema):
    """
    Crea un nuevo ejercicio.
    """
    return conversacion_controller.create_ejercicio(ejercicio_data.dict())


@router.put("/ejercicios/{ejercicio_id}", response_model=str)
def update_ejercicio(ejercicio_id: str, ejercicio_data: EjerciciosSchema):
    """
    Actualiza un ejercicio existente.
    """
    return conversacion_controller.update_ejercicio(ejercicio_id, ejercicio_data.dict())


@router.delete("/ejercicios/{ejercicio_id}", response_model=str)
def delete_ejercicio(ejercicio_id: str):
    """
    Elimina un ejercicio por su ID.
    """
    return conversacion_controller.delete_ejercicio(ejercicio_id)  


@router.get("/ejercicios/usuario/{usuario_id}", response_model=list[EjerciciosSchema])
def get_ejercicios_by_usuario(usuario_id: str):
    """
    Obtiene todos los ejercicios asociados a un usuario.
    """
    return conversacion_controller.get_ejercicios_by_usuario(usuario_id)


@router.get("/ejercicios/conversacion/{conversacion_id}", response_model=list[EjerciciosSchema])
def get_ejercicios_by_conversacion(registro_id: str):
    """
    Obtiene todos los ejercicios asociados a un registro de conversación.
    """
    return conversacion_controller.get_ejercicios_by_conversacion(registro_id)
