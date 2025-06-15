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

# --- Funciones CRUD para Logros ---

async def get_logro_by_id(db: AsyncIOMotorDatabase, logro_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene un logro por su ID de la base de datos.
    """
    try:
        if not ObjectId.is_valid(logro_id):
            print(f"ERROR (Controller): ID de logro inválido: {logro_id}")
            return None

        logro = await db.logros.find_one({"_id": ObjectId(logro_id)})
        if logro:
            processed_logro = _convert_id_to_str(logro)
            print(f"DEBUG (Controller): Logro recuperado por ID ({logro_id}): {processed_logro}")
            return processed_logro
        print(f"DEBUG (Controller): Logro no encontrado para ID: {logro_id}")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar el logro '{logro_id}': {e}")
        return None


async def get_all_logros(db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
    """
    Obtiene todos los logros de la base de datos.
    """
    try:
        logros = await db.logros.find().to_list(None)
        processed_logros = [_convert_id_to_str(l) for l in logros]
        if not processed_logros:
            print("DEBUG (Controller): No se encontraron logros.")
        
        print(f"DEBUG (Controller): Logros recuperados: {processed_logros}")
        return processed_logros
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar los logros: {e}")
        return []


async def create_logro(db: AsyncIOMotorDatabase, logro_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Crea un nuevo logro en la base de datos.
    """
    try:
        if "fecha_logro" in logro_data and isinstance(logro_data["fecha_logro"], str):
             logro_data["fecha_logro"] = datetime.fromisoformat(logro_data["fecha_logro"])

        result = await db.logros.insert_one(logro_data)
        
        if not result.acknowledged:
            print("ERROR (Controller): Fallo en el reconocimiento de la inserción de logro.")
            return None
        
        created_logro = await db.logros.find_one({"_id": result.inserted_id})
        if created_logro:
            processed_logro = _convert_id_to_str(created_logro)
            print(f"DEBUG (Controller): Logro creado: {processed_logro}")
            return processed_logro
        print("ERROR (Controller): No se pudo recuperar el logro recién creado.")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al crear el logro: {e}")
        return None


async def update_logro(db: AsyncIOMotorDatabase, logro_id: str, logro_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Actualiza un logro existente en la base de datos.
    """
    try:
        if not ObjectId.is_valid(logro_id):
            print(f"ERROR (Controller): ID de logro inválido: {logro_id}")
            return None

        object_id = ObjectId(logro_id)
        
        logro_data.pop('id', None)
        logro_data.pop('_id', None)

        await db.logros.update_one(
            {"_id": object_id},
            {"$set": logro_data}
        )
        
        updated_logro = await db.logros.find_one({"_id": object_id})
        if updated_logro:
            processed_logro = _convert_id_to_str(updated_logro)
            print(f"DEBUG (Controller): Logro actualizado: {processed_logro}")
            return processed_logro
        print(f"DEBUG (Controller): Logro no encontrado o no se pudo recuperar después de la actualización para ID: {logro_id}")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al actualizar el logro '{logro_id}': {e}")
        return None


async def delete_logro(db: AsyncIOMotorDatabase, logro_id: str) -> bool:
    """
    Elimina un logro por su ID de la base de datos.
    """
    try:
        if not ObjectId.is_valid(logro_id):
            print(f"ERROR (Controller): ID de logro inválido: {logro_id}")
            return False

        result = await db.logros.delete_one({"_id": ObjectId(logro_id)})
        
        if result.deleted_count == 0:
            print(f"DEBUG (Controller): Logro no encontrado para eliminar con ID: {logro_id}")
            return False
        
        print(f"DEBUG (Controller): Logro eliminado ({logro_id}): True")
        return True
    except Exception as e:
        print(f"ERROR (Controller): Error al eliminar el logro '{logro_id}': {e}")
        return False


async def get_logros_by_usuario(db: AsyncIOMotorDatabase, usuario_id: str) -> List[Dict[str, Any]]:
    """
    Busca los logros de un usuario específico.
    """
    try:
        query_user_id = usuario_id

        logros = await db.logros.find({"usuario_id": query_user_id}).to_list(None)
        
        processed_logros = [_convert_id_to_str(l) for l in logros]
        if not processed_logros:
            print(f"DEBUG (Controller): No se encontraron logros para el usuario {usuario_id}")
        
        print(f"DEBUG (Controller): Logros para usuario {usuario_id}: {processed_logros}")
        return processed_logros
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar los logros del usuario '{usuario_id}': {e}")
        return []


async def get_logros_tipo(db: AsyncIOMotorDatabase, usuario_id: str, tipo: str) -> List[Dict[str, Any]]:
    """
    Busca los logros de un usuario por tipo específico.
    """
    try:
        query_user_id = usuario_id

        logros = await db.logros.find({"usuario_id": query_user_id, "tipo": tipo}).to_list(None)
        
        processed_logros = [_convert_id_to_str(l) for l in logros]
        if not processed_logros:
            print(f"DEBUG (Controller): No se encontraron logros del tipo '{tipo}' para el usuario {usuario_id}")
        
        print(f"DEBUG (Controller): Logros de tipo '{tipo}' para usuario {usuario_id}: {processed_logros}")
        return processed_logros
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar los logros del tipo '{tipo}' del usuario '{usuario_id}': {e}")
        return []
