from fastapi import APIRouter, HTTPException, status, Response, Depends
from controllers import registro_controller # Tu controlador corregido
from schemas.registro_schema import RegistroCreate, RegistroResponse # Nuevos esquemas
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
from dotenv import load_dotenv
from connection.database import Database # Importa la clase Database
from datetime import datetime # Para tipos de fecha en path params

load_dotenv()
DB_NAME = os.getenv("DB_NAME")

router = APIRouter()

# Función de dependencia para obtener la instancia de la base de datos
async def get_database_instance() -> AsyncIOMotorDatabase:
    if Database.client is None:
        raise HTTPException(status_code=500, detail="Database client not initialized")
    return Database.client[DB_NAME]

@router.get("/{registro_id}", response_model=RegistroResponse, status_code=status.HTTP_200_OK)
async def get_registro(registro_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene un registro por su ID.
    """
    registro = await registro_controller.get_registro_by_id(db, registro_id)
    if registro is None:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return registro


@router.get("/", response_model=List[RegistroResponse], status_code=status.HTTP_200_OK)
async def get_all_registros(db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene todos los registros.
    """
    registros = await registro_controller.get_all_registros(db)
    if not registros: # Opcional: lanzar 404 si no hay ninguno. Considera 200 con lista vacía.
            raise HTTPException(status_code=404, detail="No se encontraron registros") # Quitar esta línea si prefieres 200 con lista vacía
    return registros


@router.post("/", response_model=RegistroResponse, status_code=status.HTTP_201_CREATED) # Retorna el objeto creado
async def create_registro(registro_data: RegistroCreate, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Crea un nuevo registro.
    """
    created_registro = await registro_controller.create_registro(db, registro_data.model_dump())
    if created_registro is None:
        raise HTTPException(status_code=500, detail="Error al crear el registro.")
    return created_registro


@router.put("/{registro_id}", response_model=RegistroResponse, status_code=status.HTTP_200_OK) # Retorna el objeto actualizado
async def update_registro(registro_id: str, registro_data: RegistroCreate, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Actualiza un registro existente.
    """
    updated_registro = await registro_controller.update_registro(db, registro_id, registro_data.model_dump(exclude_unset=True))
    if updated_registro is None:
        raise HTTPException(status_code=404, detail="Registro no encontrado o error al actualizar.")
    return updated_registro


@router.delete("/{registro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registro(registro_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Elimina un registro por su ID.
    """
    success = await registro_controller.delete_registro(db, registro_id)
    if not success:
        raise HTTPException(status_code=404, detail="Registro no encontrado o error al eliminar")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/usuario/{usuario_id}", response_model=List[RegistroResponse], status_code=status.HTTP_200_OK) # Nueva ruta, importante para Streamlit
async def get_registros_for_usuario(usuario_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene todos los registros para un usuario específico.
    """
    registros = await registro_controller.get_registros_by_usuario(db, usuario_id)
    if not registros:
        # Puedes devolver un 200 con lista vacía o un 404 si es un recurso que siempre debe existir
        raise HTTPException(status_code=404, detail=f"No se encontraron registros para el usuario {usuario_id}")
    return registros


@router.get("/historial/{usuario_id}/{ejercicio_nombre}", response_model=List[RegistroResponse], tags=["Historial"])
async def get_historial_for_ejercicio(usuario_id: str, ejercicio_nombre: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene el historial de registros para un ejercicio específico de un usuario.
    """
    historial = await registro_controller.get_historial_por_ejercicio(db, usuario_id, ejercicio_nombre)
    if not historial:
        raise HTTPException(status_code=404, detail=f"No se encontraron registros para el ejercicio '{ejercicio_nombre}' del usuario {usuario_id}")
    return historial


@router.get("/fecha/{usuario_id}/{fecha_inicio}/{fecha_fin}", response_model=List[RegistroResponse], tags=["Historial"])
async def get_registros_by_date_range(
    usuario_id: str, 
    fecha_inicio: str, # Recibir como string, convertir a datetime en controller
    fecha_fin: str,    # Recibir como string, convertir a datetime en controller
    db: AsyncIOMotorDatabase = Depends(get_database_instance)
):
    """
    Obtiene los registros de un usuario dentro de un rango de fechas.
    """
    # Convertir las fechas a objetos datetime aquí, o asegurarse que el controlador las maneja
    # Si tu controlador espera datetime directamente, puedes convertir aquí:
    try:
        fecha_inicio_dt = datetime.fromisoformat(fecha_inicio)
        fecha_fin_dt = datetime.fromisoformat(fecha_fin)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD o ISO 8601.")

    registros = await registro_controller.get_registros_por_fecha(db, usuario_id, fecha_inicio_dt, fecha_fin_dt)
    if not registros:
        raise HTTPException(status_code=404, detail="No se encontraron registros en el rango de fechas especificado")
    return registros
