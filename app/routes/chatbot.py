from fastapi import APIRouter, HTTPException, status, Response, Depends
from controllers import conversacion_controller # Tu controlador corregido
from schemas.conversacion_schema import ConversacionCreate, ConversacionResponse # Nuevos esquemas
from typing import List, Dict
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

@router.get("/{conversacion_id}", response_model=ConversacionResponse, status_code=status.HTTP_200_OK)
async def get_conversacion(conversacion_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene una conversación por su ID.
    """
    conversacion = await conversacion_controller.get_conversacion_by_id(db, conversacion_id)
    if conversacion is None:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return conversacion


@router.get("/", response_model=List[ConversacionResponse], status_code=status.HTTP_200_OK)
async def get_all_conversaciones(db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene todas las conversaciones.
    """
    conversaciones = await conversacion_controller.get_all_conversaciones(db)
    if not conversaciones: # Opcional: lanzar 404 si no hay ninguno. Considera 200 con lista vacía.
        raise HTTPException(status_code=404, detail="No se encontraron conversaciones") # Quitar esta línea si prefieres 200 con lista vacía
    return conversaciones


@router.post("/", response_model=ConversacionResponse, status_code=status.HTTP_201_CREATED) # Retorna el objeto creado
async def create_conversacion(conversacion_data: ConversacionCreate, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Crea una nueva conversación.
    """
    created_conversacion = await conversacion_controller.create_conversacion(db, conversacion_data.model_dump())
    if created_conversacion is None:
        raise HTTPException(status_code=500, detail="Error al crear la conversación.")
    return created_conversacion


@router.put("/{conversacion_id}", response_model=ConversacionResponse, status_code=status.HTTP_200_OK) # Retorna el objeto actualizado
async def update_conversacion(conversacion_id: str, conversacion_data: ConversacionCreate, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Actualiza una conversación existente.
    """
    updated_conversacion = await conversacion_controller.update_conversacion(db, conversacion_id, conversacion_data.model_dump(exclude_unset=True))
    if updated_conversacion is None:
        raise HTTPException(status_code=404, detail="Conversación no encontrada o no se realizaron cambios.")
    return updated_conversacion


@router.delete("/{conversacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversacion(conversacion_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Elimina una conversación por su ID.
    """
    success = await conversacion_controller.delete_conversacion(db, conversacion_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversación no encontrada o error al eliminar")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Rutas específicas para el chatbot/conversaciones
@router.get("/ultimos_mensajes/{usuario_id}/{n_mensajes}", response_model=List[ConversacionResponse], tags=["Chatbot"])
async def get_latest_messages_for_user(usuario_id: str, n_mensajes: int, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene los últimos N mensajes de un usuario.
    """
    messages = await conversacion_controller.get_ultimos_mensajes(db, usuario_id, n_mensajes)
    if not messages:
        raise HTTPException(status_code=404, detail=f"No se encontraron mensajes recientes para el usuario {usuario_id}")
    return messages


@router.get("/por_tema/{usuario_id}/{tema}", response_model=List[ConversacionResponse], tags=["Chatbot"])
async def get_messages_by_topic_for_user(usuario_id: str, tema: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Obtiene mensajes de un usuario filtrados por tema.
    """
    messages = await conversacion_controller.get_mensajes_por_tema(db, usuario_id, tema)
    if not messages:
        raise HTTPException(status_code=404, detail=f"No se encontraron mensajes sobre el tema '{tema}' para el usuario {usuario_id}")
    return messages


@router.get("/analizar_estado_animo/{usuario_id}", response_model=Dict[str, str], tags=["Chatbot"])
async def analyze_user_mood(usuario_id: str, db: AsyncIOMotorDatabase = Depends(get_database_instance)):
    """
    Analiza el estado de ánimo de un usuario basado en sus conversaciones.
    """
    mood_analysis = await conversacion_controller.analizar_estado_animo(db, usuario_id)
    # El controlador ya maneja si no hay conversaciones devolviendo un dict,
    # así que no necesitamos un HTTPException aquí a menos que el controlador falle de otra manera.
    return mood_analysis
    