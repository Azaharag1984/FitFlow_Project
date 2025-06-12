from fastapi import APIRouter
from controllers import ejercicio_controller
from schemas.ejercicio_schema import EjercicioBase

router = APIRouter()


@router.get("/ejercicios/{ejercicio_id}", response_model=EjercicioBase)
def get_ejercicio(ejercicio_id: str):
    """
    Obtiene un ejercicio por su ID.
    """
    return ejercicio_controller.get_ejercicio_by_id(ejercicio_id)


@router.get("/ejercicios", response_model=list[EjercicioBase])
def get_all_ejercicios():
    """
    Obtiene todos los ejercicios.
    """
    return ejercicio_controller.get_all_ejercicios()


@router.post("/ejercicios", response_model=str)
def create_ejercicio(ejercicio_data: EjercicioBase):
    """
    Crea un nuevo ejercicio.
    """
    return ejercicio_controller.create_ejercicio(ejercicio_data.dict())


@router.put("/ejercicios/{ejercicio_id}", response_model=str)
def update_ejercicio(ejercicio_id: str, ejercicio_data: EjercicioBase):
    """
    Actualiza un ejercicio existente.
    """
    return ejercicio_controller.update_ejercicio(ejercicio_id, ejercicio_data.dict())


@router.delete("/ejercicios/{ejercicio_id}", response_model=str)
def delete_ejercicio(ejercicio_id: str):
    """
    Elimina un ejercicio por su ID.
    """
    return ejercicio_controller.delete_ejercicio(ejercicio_id)  


@router.get("/ejercicios/usuario/{usuario_id}", response_model=list[EjercicioBase])
def get_ejercicios_by_usuario(usuario_id: str):
    """
    Obtiene todos los ejercicios asociados a un usuario.
    """
    return ejercicio_controller.get_ejercicios_by_usuario(usuario_id)


@router.get("/ejercicios/ejercicio/{ejercicio_id}", response_model=list[EjercicioBase])
def get_ejercicios_by_ejercicio(ejercicio_id: str):
    """
    Obtiene todos los ejercicios asociados a un ejercicio de conversación.
    """
    return ejercicio_controller.get_ejercicios_by_ejercicio(ejercicio_id)
