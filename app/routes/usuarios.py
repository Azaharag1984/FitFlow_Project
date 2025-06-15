from fastapi import APIRouter, HTTPException, status, Response, Depends
from controllers import usuario_controller
from schemas.usuario_schema import UsuarioCreate, UsuarioResponse
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

@router.get("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
async def get_usuario(usuario_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)): # Inyección de dependencia
    """
    Obtiene un usuario por su ID.
    """
    user = await usuario_controller.get_usuario_by_id(db, usuario_id) # Pasamos la instancia db
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("/", response_model=List[UsuarioResponse], status_code=status.HTTP_200_OK)
async def get_all_usuarios(db: AsyncIOMotorDatabase = Depends(get_database_instance)): # Inyección de dependencia
    """
    Obtiene todos los usuarios.
    """
    users = await usuario_controller.get_all_usuarios(db) # ¡IMPORTANTE: Aquí se pasa 'db'!
    return users


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(usuario_data: UsuarioCreate, db: AsyncIOMotorDatabase = Depends(get_database_instance)): # Inyección de dependencia
    """
    Crea un nuevo usuario.
    """
    created_user = await usuario_controller.create_usuario(db, usuario_data.model_dump())
    if created_user:
        return created_user
    raise HTTPException(status_code=500, detail="Error al crear el usuario en el controlador.")


@router.put("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
async def update_usuario(usuario_id: str, usuario_data: UsuarioCreate, db: AsyncIOMotorDatabase = Depends(get_database_instance)): # Inyección de dependencia
    """
    Actualiza un usuario existente.
    """
    updated_user = await usuario_controller.update_usuario(db, usuario_id, usuario_data.model_dump(exclude_unset=True))
    if updated_user:
        return updated_user
    raise HTTPException(status_code=404, detail="Usuario no encontrado o error al actualizar.")


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(usuario_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)): # Inyección de dependencia
    """
    Elimina un usuario por su ID.
    """
    success = await usuario_controller.delete_usuario(db, usuario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o error al eliminar")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{usuario_id}/progreso", tags=["Progreso"])
async def obtener_ultimo_peso_por_ejercicio(usuario_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)): # Inyección de dependencia
    """
    Obtiene el último peso registrado por ejercicio para un usuario.
    """
    return await usuario_controller.get_ultimo_peso_por_ejercicio(db, usuario_id)


@router.get("/{usuario_id}/progreso/{ejercicio_nombre}/mejor_marca", tags=["Progreso"])
async def obtener_mejor_marca(usuario_id: str, ejercicio_nombre: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)): # Inyección de dependencia
    """
    Obtiene la mejor marca de un ejercicio específico para un usuario.
    """
    return await usuario_controller.get_mejor_marca(db, usuario_id, ejercicio_nombre)


@router.get("/{usuario_id}/progreso/frecuencia_semanal", tags=["Progreso"])
async def obtener_frecuencia_semanal(usuario_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)): # Inyección de dependencia
    """
    Obtiene la frecuencia semanal de registros de un usuario.
    """
    return await usuario_controller.get_frecuencia_semanal(db, usuario_id)


@router.get("/{usuario_id}/progreso/volumen_total", tags=["Progreso"])
async def obtener_volumen_total(usuario_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)): # Inyección de dependencia
    """
    Obtiene el volumen total de levantamiento de un usuario.
    """
    return await usuario_controller.get_volumen_total(db, usuario_id)

