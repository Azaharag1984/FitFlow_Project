from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

# --- Función auxiliar para convertir ObjectId a str de forma recursiva ---
def _convert_id_to_str(document: Any) -> Any:
    """
    Convierte ObjectId en str dentro de un diccionario o lista de diccionarios.
    Útil para la serialización de respuestas de la API.
    """
    if isinstance(document, dict):
        return {
            k: str(v) if isinstance(v, ObjectId) else _convert_id_to_str(v)
            for k, v in document.items()
        }
    elif isinstance(document, list):
        return [_convert_id_to_str(elem) for elem in document]
    elif isinstance(document, ObjectId):
        return str(document)
    return document

# --- Funciones CRUD para Conversaciones ---

async def get_conversacion_by_id(db: AsyncIOMotorDatabase, conversacion_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene una conversación por su ID de la base de datos.
    """
    try:
        if not ObjectId.is_valid(conversacion_id):
            print(f"ERROR (Controller): ID de conversación inválido: {conversacion_id}")
            return None

        conversacion = await db.conversaciones.find_one({"_id": ObjectId(conversacion_id)})
        if conversacion:
            processed_conversacion = _convert_id_to_str(conversacion)
            print(f"DEBUG (Controller): Conversación recuperada por ID ({conversacion_id}): {processed_conversacion}")
            return processed_conversacion
        print(f"DEBUG (Controller): Conversación no encontrada para ID: {conversacion_id}")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar la conversación '{conversacion_id}': {e}")
        return None


async def get_all_conversaciones(db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
    """
    Obtiene todas las conversaciones de la base de datos.
    """
    try:
        conversaciones = await db.conversaciones.find().to_list(None)
        processed_conversaciones = [_convert_id_to_str(c) for c in conversaciones]
        if not processed_conversaciones:
            print("DEBUG (Controller): No se encontraron conversaciones.")
        
        print(f"DEBUG (Controller): Conversaciones recuperadas: {processed_conversaciones}")
        return processed_conversaciones
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar las conversaciones: {e}")
        return []


async def create_conversacion(db: AsyncIOMotorDatabase, conversacion_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Crea una nueva conversación en la base de datos.
    """
    try:
        result = await db.conversaciones.insert_one(conversacion_data)
        
        if not result.acknowledged:
            print("ERROR (Controller): Fallo en el reconocimiento de la inserción de conversación.")
            return None
        
        created_conversacion = await db.conversaciones.find_one({"_id": result.inserted_id})
        if created_conversacion:
            processed_conversacion = _convert_id_to_str(created_conversacion)
            print(f"DEBUG (Controller): Conversación creada: {processed_conversacion}")
            return processed_conversacion
        print("ERROR (Controller): No se pudo recuperar la conversación recién creada.")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al crear la conversación: {e}")
        return None


async def update_conversacion(db: AsyncIOMotorDatabase, conversacion_id: str, conversacion_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Actualiza una conversación existente en la base de datos.
    """
    try:
        if not ObjectId.is_valid(conversacion_id):
            print(f"ERROR (Controller): ID de conversación inválido: {conversacion_id}")
            return None

        object_id = ObjectId(conversacion_id)
        
        conversacion_data.pop('id', None)
        conversacion_data.pop('_id', None)

        await db.conversaciones.update_one(
            {"_id": object_id},
            {"$set": conversacion_data}
        )
        
        updated_conversacion = await db.conversaciones.find_one({"_id": object_id})
        if updated_conversacion:
            processed_conversacion = _convert_id_to_str(updated_conversacion)
            print(f"DEBUG (Controller): Conversación actualizada: {processed_conversacion}")
            return processed_conversacion
        print(f"DEBUG (Controller): Conversación no encontrada o no se pudo recuperar después de la actualización para ID: {conversacion_id}")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al actualizar la conversación '{conversacion_id}': {e}")
        return None


async def delete_conversacion(db: AsyncIOMotorDatabase, conversacion_id: str) -> bool:
    """
    Elimina una conversación por su ID de la base de datos.
    """
    try:
        if not ObjectId.is_valid(conversacion_id):
            print(f"ERROR (Controller): ID de conversación inválido: {conversacion_id}")
            return False
        
        result = await db.conversaciones.delete_one({"_id": ObjectId(conversacion_id)})
        
        if result.deleted_count == 0:
            print(f"DEBUG (Controller): Conversación no encontrada para eliminar con ID: {conversacion_id}")
            return False
        
        print(f"DEBUG (Controller): Conversación eliminada ({conversacion_id}): True")
        return True
    except Exception as e:
        print(f"ERROR (Controller): Error al eliminar la conversación '{conversacion_id}': {e}")
        return False


# --- Funciones de Consulta Específicas para Chatbot ---

async def get_conversaciones_by_usuario(db: AsyncIOMotorDatabase, usuario_id: str) -> List[Dict[str, Any]]:
    """
    Busca conversaciones de un usuario específico.
    """
    try:
        query_user_id = usuario_id

        conversaciones = await db.conversaciones.find({"usuario_id": query_user_id}).to_list(None)
        
        processed_conversaciones = [_convert_id_to_str(c) for c in conversaciones]
        if not processed_conversaciones:
            print(f"DEBUG (Controller): No se encontraron conversaciones para el usuario {usuario_id}")
        
        print(f"DEBUG (Controller): Conversaciones para usuario {usuario_id}: {processed_conversaciones}")
        return processed_conversaciones
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar las conversaciones del usuario '{usuario_id}': {e}")
        return []


async def get_ultimos_mensajes(db: AsyncIOMotorDatabase, usuario_id: str, n: int) -> List[Dict[str, Any]]:
    """
    Obtiene los últimos n mensajes de un usuario.
    """
    try:
        query_user_id = usuario_id

        mensajes = await db.conversaciones.find({"usuario_id": query_user_id}).sort("fecha", -1).limit(n).to_list(None)
        
        processed_mensajes = [_convert_id_to_str(m) for m in mensajes]
        if not processed_mensajes:
            print(f"DEBUG (Controller): No se encontraron mensajes recientes para el usuario {usuario_id}")
        
        print(f"DEBUG (Controller): Últimos {n} mensajes para usuario {usuario_id}: {processed_mensajes}")
        return processed_mensajes
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar los últimos mensajes del usuario '{usuario_id}': {e}")
        return []


async def get_mensajes_por_tema(db: AsyncIOMotorDatabase, usuario_id: str, tema: str) -> List[Dict[str, Any]]:
    """
    Obtiene mensajes relacionados con un tema específico para un usuario.
    """
    try:
        query_user_id = usuario_id

        mensajes = await db.conversaciones.find({
            "usuario_id": query_user_id,
            "tema": tema
        }).to_list(None)
        
        processed_mensajes = [_convert_id_to_str(m) for m in mensajes]
        if not processed_mensajes:
            print(f"DEBUG (Controller): No se encontraron mensajes sobre el tema '{tema}' para el usuario {usuario_id}")
        
        print(f"DEBUG (Controller): Mensajes por tema '{tema}' para usuario {usuario_id}: {processed_mensajes}")
        return processed_mensajes
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar los mensajes por tema para el usuario '{usuario_id}': {e}")
        return []


async def analizar_estado_animo(db: AsyncIOMotorDatabase, usuario_id: str) -> Dict[str, str]:
    """
    Analiza el estado de ánimo de un usuario basado en sus conversaciones.
    (Esta es una lógica de PLACEHOLDER; necesitarías integrar un modelo de PNL real aquí).
    """
    try:
        query_user_id = usuario_id

        conversaciones = await db.conversaciones.find({"usuario_id": query_user_id}).to_list(None)
        
        # No es necesario convertir aquí ya que el resultado final es un dict de strings,
        # pero si la lógica del análisis dependiera de atributos ObjectId, se haría aquí.
        
        if not conversaciones:
            print(f"DEBUG (Controller): No se encontraron conversaciones para el usuario {usuario_id} para analizar estado de ánimo.")
            return {"estado_animo": "No disponible"}
        
        estado_animo = "Neutral"
        if any("triste" in msg.get("mensaje", "").lower() for msg in conversaciones):
            estado_animo = "Negativo"
        elif any("feliz" in msg.get("mensaje", "").lower() for msg in conversaciones):
            estado_animo = "Positivo"
            
        print(f"DEBUG (Controller): Estado de ánimo analizado para {usuario_id}: {estado_animo}")
        return {"estado_animo": estado_animo}
    except Exception as e:
        print(f"ERROR (Controller): Error al analizar el estado de ánimo del usuario '{usuario_id}': {e}")
        return {"estado_animo": "Error al analizar"}
