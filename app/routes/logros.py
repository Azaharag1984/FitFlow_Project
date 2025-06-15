from fastapi import APIRouter, HTTPException, status, Response, Depends
from controllers import logro_controller # Tu controlador corregido
from schemas.logro_schema import LogroCreate, LogroResponse # Nuevos esquemas
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
from dotenv import load_dotenv
from connection.database import Database # Importa la clase Database
from datetime import datetime # Para tipos de fecha si se usan en path params

load_dotenv()
DB_NAME = os.getenv("DB_NAME")

router = APIRouter()

# Función de dependencia para obtener la instancia de la base de datos
async def get_database_instance() -> AsyncIOMotorDatabase:
    if Database.client is None:
        raise HTTPException(status_code=500, detail="Database client not initialized")
    return Database.client[DB_NAME]

@router.get("/{logro_id}", response_model=LogroResponse, status_code=status.HTTP_200_OK)
async def get_logro(logro_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene un logro por su ID.
    """
    logro = await logro_controller.get_logro_by_id(db, logro_id)
    if logro is None:
        raise HTTPException(status_code=404, detail="Logro no encontrado")
    return logro


@router.get("/", response_model=List[LogroResponse], status_code=status.HTTP_200_OK)
async def get_all_logros(db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene todos los logros.
    """
    logros = await logro_controller.get_all_logros(db)
    if not logros: # Opcional: lanzar 404 si no hay ninguno. Considera 200 con lista vacía.
        raise HTTPException(status_code=404, detail="No se encontraron logros") # Quitar esta línea si prefieres 200 con lista vacía
    return logros


@router.post("/", response_model=LogroResponse, status_code=status.HTTP_201_CREATED) # Retorna el objeto creado
async def create_logro(logro_data: LogroCreate, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Crea un nuevo logro.
    """
    created_logro = await logro_controller.create_logro(db, logro_data.model_dump())
    if created_logro is None:
        raise HTTPException(status_code=500, detail="Error al crear el logro.")
    return created_logro


@router.put("/{logro_id}", response_model=LogroResponse, status_code=status.HTTP_200_OK) # Retorna el objeto actualizado
async def update_logro(logro_id: str, logro_data: LogroCreate, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Actualiza un logro existente.
    """
    updated_logro = await logro_controller.update_logro(db, logro_id, logro_data.model_dump(exclude_unset=True))
    if updated_logro is None:
        raise HTTPException(status_code=404, detail="Logro no encontrado o error al actualizar.")
    return updated_logro


@router.delete("/{logro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_logro(logro_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Elimina un logro por su ID.
    """
    success = await logro_controller.delete_logro(db, logro_id)
    if not success:
        raise HTTPException(status_code=404, detail="Logro no encontrado o error al eliminar")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/usuario/{usuario_id}", response_model=List[LogroResponse], tags=["Logros por Usuario"])
async def get_logros_for_usuario(usuario_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene todos los logros para un usuario específico.
    """
    logros = await logro_controller.get_logros_by_usuario(db, usuario_id)
    if not logros:
        raise HTTPException(status_code=404, detail=f"No se encontraron logros para el usuario {usuario_id}")
    return logros


@router.get("/usuario/{usuario_id}/tipo/{tipo}", response_model=List[LogroResponse], tags=["Logros por Tipo"])
async def get_logros_by_type_for_usuario(usuario_id: str, tipo: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene los logros de un usuario filtrados por tipo.
    """
    logros = await logro_controller.get_logros_tipo(db, usuario_id, tipo)
    if not logros:
        raise HTTPException(status_code=404, detail=f"No se encontraron logros del tipo '{tipo}' para el usuario {usuario_id}")
    return logros
