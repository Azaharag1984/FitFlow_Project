from bson import ObjectId
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

# --- Funciones CRUD para Ejercicios ---

async def get_ejercicio_by_id(db: AsyncIOMotorDatabase, ejercicio_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene un ejercicio por su ID de la base de datos.
    """
    try:
        if not ObjectId.is_valid(ejercicio_id):
            print(f"ERROR (Controller): ID de ejercicio inválido: {ejercicio_id}")
            return None

        ejercicio = await db.ejercicios.find_one({"_id": ObjectId(ejercicio_id)})
        if ejercicio:
            processed_ejercicio = _convert_id_to_str(ejercicio)
            print(f"DEBUG (Controller): Ejercicio recuperado por ID ({ejercicio_id}): {processed_ejercicio}")
            return processed_ejercicio
        print(f"DEBUG (Controller): Ejercicio no encontrado para ID: {ejercicio_id}")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar el ejercicio '{ejercicio_id}': {e}")
        return None


async def get_all_ejercicios(db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
    """
    Obtiene todos los ejercicios de la base de datos.
    """
    try:
        ejercicios = await db.ejercicios.find().to_list(None)
        processed_ejercicios = [_convert_id_to_str(e) for e in ejercicios]
        if not processed_ejercicios:
            print("DEBUG (Controller): No se encontraron ejercicios.")
        
        print(f"DEBUG (Controller): Ejercicios recuperados: {processed_ejercicios}")
        return processed_ejercicios
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar los ejercicios: {e}")
        return []


async def create_ejercicio(db: AsyncIOMotorDatabase, ejercicio_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Crea un nuevo ejercicio en la base de datos.
    """
    try:
        result = await db.ejercicios.insert_one(ejercicio_data)
        
        if not result.acknowledged:
            print("ERROR (Controller): Fallo en el reconocimiento de la inserción de ejercicio.")
            return None
        
        created_ejercicio = await db.ejercicios.find_one({"_id": result.inserted_id})
        if created_ejercicio:
            processed_ejercicio = _convert_id_to_str(created_ejercicio)
            print(f"DEBUG (Controller): Ejercicio creado: {processed_ejercicio}")
            return processed_ejercicio
        print("ERROR (Controller): No se pudo recuperar el ejercicio recién creado.")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al crear el ejercicio: {e}")
        return None


async def update_ejercicio(db: AsyncIOMotorDatabase, ejercicio_id: str, ejercicio_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Actualiza un ejercicio existente en la base de datos.
    """
    try:
        if not ObjectId.is_valid(ejercicio_id):
            print(f"ERROR (Controller): ID de ejercicio inválido: {ejercicio_id}")
            return None

        object_id = ObjectId(ejercicio_id)
        
        ejercicio_data.pop('id', None)
        ejercicio_data.pop('_id', None)

        await db.ejercicios.update_one(
            {"_id": object_id},
            {"$set": ejercicio_data}
        )
        
        updated_ejercicio = await db.ejercicios.find_one({"_id": object_id})
        if updated_ejercicio:
            processed_ejercicio = _convert_id_to_str(updated_ejercicio)
            print(f"DEBUG (Controller): Ejercicio actualizado: {processed_ejercicio}")
            return processed_ejercicio
        print(f"DEBUG (Controller): Ejercicio no encontrado o no se pudo recuperar después de la actualización para ID: {ejercicio_id}")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al actualizar el ejercicio '{ejercicio_id}': {e}")
        return None


async def delete_ejercicio(db: AsyncIOMotorDatabase, ejercicio_id: str) -> bool:
    """
    Elimina un ejercicio por su ID de la base de datos.
    """
    try:
        if not ObjectId.is_valid(ejercicio_id):
            print(f"ERROR (Controller): ID de ejercicio inválido: {ejercicio_id}")
            return False

        result = await db.ejercicios.delete_one({"_id": ObjectId(ejercicio_id)})
        
        if result.deleted_count == 0:
            print(f"DEBUG (Controller): Ejercicio no encontrado para eliminar con ID: {ejercicio_id}")
            return False
        
        print(f"DEBUG (Controller): Ejercicio eliminado ({ejercicio_id}): True")
        return True
    except Exception as e:
        print(f"ERROR (Controller): Error al eliminar el ejercicio '{ejercicio_id}': {e}")
        return False


async def get_ejercicios_by_usuario(db: AsyncIOMotorDatabase, usuario_id: str) -> List[Dict[str, Any]]:
    """
    Busca ejercicios asociados a un usuario.
    """
    try:
        if not ObjectId.is_valid(usuario_id):
            print(f"ERROR (Controller): ID de usuario inválido: {usuario_id}")
            return []

        ejercicios = await db.ejercicios.find({"usuario_id": ObjectId(usuario_id)}).to_list(None)
        
        processed_ejercicios = [_convert_id_to_str(e) for e in ejercicios]
        if not processed_ejercicios:
            print(f"DEBUG (Controller): No se encontraron ejercicios para el usuario {usuario_id}.")
        
        print(f"DEBUG (Controller): Ejercicios para usuario {usuario_id}: {processed_ejercicios}")
        return processed_ejercicios
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar los ejercicios del usuario '{usuario_id}': {e}")
        return []


async def get_ejercicios_by_conversacion(db: AsyncIOMotorDatabase, conversacion_id: str) -> List[Dict[str, Any]]:
    """
    Busca ejercicios asociados a una conversación.
    """
    try:
        if not ObjectId.is_valid(conversacion_id):
            print(f"ERROR (Controller): ID de conversación inválido: {conversacion_id}")
            return []

        ejercicios = await db.ejercicios.find({"conversacion_id": ObjectId(conversacion_id)}).to_list(None)
        
        processed_ejercicios = [_convert_id_to_str(e) for e in ejercicios]
        if not processed_ejercicios:
            print(f"DEBUG (Controller): No se encontraron ejercicios para la conversación {conversacion_id}.")
        
        print(f"DEBUG (Controller): Ejercicios para conversación {conversacion_id}: {processed_ejercicios}")
        return processed_ejercicios
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar los ejercicios de la conversación '{conversacion_id}': {e}")
        return []
