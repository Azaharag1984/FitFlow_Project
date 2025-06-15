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

# --- Funciones CRUD para Registros ---

async def get_registro_by_id(db: AsyncIOMotorDatabase, registro_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene un registro por su ID de la base de datos.
    """
    try:
        if not ObjectId.is_valid(registro_id):
            print(f"ERROR (Controller): ID de registro inválido: {registro_id}")
            return None

        registro = await db.registros.find_one({"_id": ObjectId(registro_id)})
        if registro:
            processed_registro = _convert_id_to_str(registro)
            print(f"DEBUG (Controller): Registro recuperado por ID ({registro_id}): {processed_registro}")
            return processed_registro
        print(f"DEBUG (Controller): Registro no encontrado para ID: {registro_id}")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar el registro '{registro_id}': {e}")
        return None


async def get_all_registros(db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
    """
    Obtiene todos los registros de la base de datos.
    """
    try:
        registros = await db.registros.find().to_list(None)
        processed_registros = [_convert_id_to_str(r) for r in registros]
        if not processed_registros:
            print("DEBUG (Controller): No se encontraron registros.")
        
        print(f"DEBUG (Controller): Registros recuperados: {processed_registros}")
        return processed_registros
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar los registros: {e}")
        return []


async def create_registro(db: AsyncIOMotorDatabase, registro_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Crea un nuevo registro en la base de datos.
    """
    try:
        if "fecha_registro" in registro_data and isinstance(registro_data["fecha_registro"], str):
            registro_data["fecha_registro"] = datetime.fromisoformat(registro_data["fecha_registro"])

        result = await db.registros.insert_one(registro_data)
        
        if not result.acknowledged:
            print("ERROR (Controller): Fallo en el reconocimiento de la inserción.")
            return None
        
        created_registro = await db.registros.find_one({"_id": result.inserted_id})
        if created_registro:
            processed_registro = _convert_id_to_str(created_registro)
            print(f"DEBUG (Controller): Registro creado: {processed_registro}")
            return processed_registro
        print("ERROR (Controller): No se pudo recuperar el registro recién creado.")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al crear el registro: {e}")
        return None


async def update_registro(db: AsyncIOMotorDatabase, registro_id: str, registro_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Actualiza un registro existente en la base de datos.
    """
    try:
        if not ObjectId.is_valid(registro_id):
            print(f"ERROR (Controller): ID de registro inválido: {registro_id}")
            return None

        object_id = ObjectId(registro_id)
        
        registro_data.pop('id', None)
        registro_data.pop('_id', None)

        await db.registros.update_one(
            {"_id": object_id},
            {"$set": registro_data}
        )
        
        updated_registro = await db.registros.find_one({"_id": object_id})
        if updated_registro:
            processed_registro = _convert_id_to_str(updated_registro)
            print(f"DEBUG (Controller): Registro actualizado: {processed_registro}")
            return processed_registro
        print(f"DEBUG (Controller): Registro no encontrado o no se pudo recuperar después de la actualización para ID: {registro_id}")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al actualizar el registro '{registro_id}': {e}")
        return None


async def delete_registro(db: AsyncIOMotorDatabase, registro_id: str) -> bool:
    """
    Elimina un registro por su ID de la base de datos.
    """
    try:
        if not ObjectId.is_valid(registro_id):
            print(f"ERROR (Controller): ID de registro inválido: {registro_id}")
            return False

        result = await db.registros.delete_one({"_id": ObjectId(registro_id)})
        
        if result.deleted_count == 0:
            print(f"DEBUG (Controller): Registro no encontrado para eliminar con ID: {registro_id}")
            return False
        
        print(f"DEBUG (Controller): Registro eliminado ({registro_id}): True")
        return True
    except Exception as e:
        print(f"ERROR (Controller): Error al eliminar el registro '{registro_id}': {e}")
        return False


async def get_registros_by_usuario(db: AsyncIOMotorDatabase, usuario_id: str) -> List[Dict[str, Any]]:
    """
    Recupera los registros de entrenamiento de un usuario específico.
    """
    try:
        # Asumimos que usuario_id se almacena como string en la colección 'registros'
        query_user_id = usuario_id

        registros = await db.registros.find({"usuario_id": query_user_id}).to_list(None)
        
        processed_registros = [_convert_id_to_str(r) for r in registros]
        if not processed_registros:
            print(f"DEBUG (Controller): No se encontraron registros para el usuario {usuario_id}")
        
        print(f"DEBUG (Controller): Registros para usuario {usuario_id}: {processed_registros}")
        return processed_registros
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar los registros del usuario '{usuario_id}': {e}")
        return []


async def get_historial_por_ejercicio(db: AsyncIOMotorDatabase, usuario_id: str, ejercicio_nombre: str) -> List[Dict[str, Any]]:
    """
    Obtiene el historial de registros para un ejercicio específico de un usuario.
    """
    try:
        query_user_id = usuario_id

        registros = await db.registros.find({
            "usuario_id": query_user_id,
            "ejercicio_nombre": ejercicio_nombre
        }).sort("fecha_registro", -1).to_list(None)

        processed_registros = [_convert_id_to_str(r) for r in registros]
        if not processed_registros:
            print(f"DEBUG (Controller): No se encontraron registros para el ejercicio '{ejercicio_nombre}' del usuario {usuario_id}")
        
        print(f"DEBUG (Controller): Historial para {ejercicio_nombre} de {usuario_id}: {processed_registros}")
        return processed_registros
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar el historial del ejercicio '{ejercicio_nombre}' para el usuario '{usuario_id}': {e}")
        return []


async def get_registros_por_fecha(db: AsyncIOMotorDatabase, usuario_id: str, fecha_inicio: datetime, fecha_fin: datetime) -> List[Dict[str, Any]]:
    """
    Obtiene los registros de un usuario dentro de un rango de fechas.
    """
    try:
        query_user_id = usuario_id

        registros = await db.registros.find({
            "usuario_id": query_user_id,
            "fecha_registro": {
                "$gte": fecha_inicio,
                "$lte": fecha_fin
            }
        }).sort("fecha_registro", -1).to_list(None)

        processed_registros = [_convert_id_to_str(r) for r in registros]
        if not processed_registros:
            print(f"DEBUG (Controller): No se encontraron registros para el usuario {usuario_id} en el rango {fecha_inicio} a {fecha_fin}")
        
        print(f"DEBUG (Controller): Registros por fecha para {usuario_id}: {processed_registros}")
        return processed_registros
    except Exception as e:
        print(f"ERROR (Controller): Error al recuperar los registros por fecha para el usuario '{usuario_id}': {e}")
        return []
