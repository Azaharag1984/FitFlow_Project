from fastapi import APIRouter, HTTPException, status, Response, Depends
from controllers import ejercicio_controller # Tu controlador corregido
from schemas.ejercicio_schema import EjercicioCreate, EjercicioResponse # Nuevos esquemas
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
from dotenv import load_dotenv
from connection.database import Database # Importa la clase Database

load_dotenv()
DB_NAME = os.getenv("DB_NAME")

router = APIRouter()

# Función de dependencia para obtener la instancia de la base de datos
async def get_database_instance() -> AsyncIOMotorDatabase:
    if Database.client is None:
        raise HTTPException(status_code=500, detail="Database client not initialized")
    return Database.client[DB_NAME]

@router.get("/{ejercicio_id}", response_model=EjercicioResponse, status_code=status.HTTP_200_OK)
async def get_ejercicio(ejercicio_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene un ejercicio por su ID.
    """
    ejercicio = await ejercicio_controller.get_ejercicio_by_id(db, ejercicio_id)
    if ejercicio is None:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    return ejercicio


@router.get("/", response_model=List[EjercicioResponse], status_code=status.HTTP_200_OK)
async def get_all_ejercicios(db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene todos los ejercicios.
    """
    ejercicios = await ejercicio_controller.get_all_ejercicios(db)
    if not ejercicios: # Opcional: lanzar 404 si no hay ninguno. Considera 200 con lista vacía.
        raise HTTPException(status_code=404, detail="No se encontraron ejercicios") # Quitar esta línea si prefieres 200 con lista vacía
    return ejercicios


@router.post("/", response_model=EjercicioResponse, status_code=status.HTTP_201_CREATED) # Retorna el objeto creado
async def create_ejercicio(ejercicio_data: EjercicioCreate, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Crea un nuevo ejercicio.
    """
    created_ejercicio = await ejercicio_controller.create_ejercicio(db, ejercicio_data.model_dump())
    if created_ejercicio is None:
        raise HTTPException(status_code=500, detail="Error al crear el ejercicio.")
    return created_ejercicio


@router.put("/{ejercicio_id}", response_model=EjercicioResponse, status_code=status.HTTP_200_OK) # Retorna el objeto actualizado
async def update_ejercicio(ejercicio_id: str, ejercicio_data: EjercicioCreate, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Actualiza un ejercicio existente.
    """
    updated_ejercicio = await ejercicio_controller.update_ejercicio(db, ejercicio_id, ejercicio_data.model_dump(exclude_unset=True))
    if updated_ejercicio is None:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado o no se realizaron cambios.")
    return updated_ejercicio


@router.delete("/{ejercicio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ejercicio(ejercicio_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Elimina un ejercicio por su ID.
    """
    success = await ejercicio_controller.delete_ejercicio(db, ejercicio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado o error al eliminar")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Rutas para obtener ejercicios por usuario o conversación
# NOTA IMPORTANTE: Estas rutas asumen que tus documentos de ejercicio en MongoDB
# incluyen los campos 'usuario_id' o 'conversacion_id'. Si los ejercicios son
# solo plantillas generales, estas funciones podrían no ser aplicables
# y los enlaces se manejarían en otras colecciones (e.g., Registros).
@router.get("/usuario/{usuario_id}", response_model=List[EjercicioResponse], tags=["Ejercicios por Usuario"])
async def get_ejercicios_by_user(usuario_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene ejercicios asociados a un usuario específico.
    """
    ejercicios = await ejercicio_controller.get_ejercicios_by_usuario(db, usuario_id)
    if not ejercicios:
        raise HTTPException(status_code=404, detail=f"No se encontraron ejercicios para el usuario {usuario_id}")
    return ejercicios


@router.get("/conversacion/{conversacion_id}", response_model=List[EjercicioResponse], tags=["Ejercicios por Conversación"])
async def get_ejercicios_by_conversation(conversacion_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene ejercicios asociados a una conversación específica.
    """
    ejercicios = await ejercicio_controller.get_ejercicios_by_conversacion(db, conversacion_id)
    if not ejercicios:
        raise HTTPException(status_code=404, detail=f"No se encontraron ejercicios para la conversación {conversacion_id}")
    return ejercicios
