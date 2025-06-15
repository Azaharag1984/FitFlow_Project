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

# --- Funciones CRUD para Usuarios ---

async def get_all_usuarios(db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
    """
    Obtiene todos los usuarios de la base de datos.
    Devuelve una lista de diccionarios que incluyen el _id.
    """
    try:
        users = await db.usuarios.find().to_list(None)
        # Asegúrate de que los _id sean str para la respuesta JSON
        processed_users = [_convert_id_to_str(user) for user in users]
        print(f"DEBUG (Controller): Usuarios recuperados: {processed_users}")
        return processed_users
    except Exception as e:
        print(f"ERROR (Controller): Error al obtener todos los usuarios: {e}")
        return []

async def get_usuario_by_id(db: AsyncIOMotorDatabase, usuario_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene un usuario por su ObjectId de la base de datos.
    """
    try:
        object_id = ObjectId(usuario_id)
        user = await db.usuarios.find_one({"_id": object_id})
        if user:
            processed_user = _convert_id_to_str(user)
            print(f"DEBUG (Controller): Usuario recuperado por ID ({usuario_id}): {processed_user}")
            return processed_user
        print(f"DEBUG (Controller): Usuario no encontrado para ID '{usuario_id}'")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al obtener usuario por ID '{usuario_id}': {e}")
        return None

async def create_usuario(db: AsyncIOMotorDatabase, usuario_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Crea un nuevo usuario en la base de datos.
    usuario_data debe ser un diccionario que NO contenga '_id'.
    """
    try:
        if "fecha_creacion" not in usuario_data or usuario_data["fecha_creacion"] is None:
            usuario_data["fecha_creacion"] = datetime.utcnow()

        result = await db.usuarios.insert_one(usuario_data)
        
        created_user = await db.usuarios.find_one({"_id": result.inserted_id})
        if created_user:
            processed_user = _convert_id_to_str(created_user)
            print(f"DEBUG (Controller): Usuario creado: {processed_user}")
            return processed_user
        print("ERROR (Controller): No se pudo recuperar el usuario recién creado.")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al crear usuario: {e}")
        return None

async def update_usuario(db: AsyncIOMotorDatabase, usuario_id: str, usuario_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Actualiza un usuario existente en la base de datos.
    usuario_data debe ser un diccionario con los campos a actualizar.
    """
    try:
        object_id = ObjectId(usuario_id)
        
        usuario_data.pop('id', None)
        usuario_data.pop('_id', None)

        result = await db.usuarios.update_one(
            {"_id": object_id},
            {"$set": usuario_data}
        )
        if result.matched_count == 0:
            print(f"DEBUG (Controller): No se encontró usuario para actualizar con ID: {usuario_id}")
            return None
        
        updated_user = await db.usuarios.find_one({"_id": object_id})
        if updated_user:
            processed_user = _convert_id_to_str(updated_user)
            print(f"DEBUG (Controller): Usuario actualizado: {processed_user}")
            return processed_user
        print(f"ERROR (Controller): No se pudo recuperar el usuario actualizado para ID: {usuario_id}")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al actualizar usuario '{usuario_id}': {e}")
        return None

async def delete_usuario(db: AsyncIOMotorDatabase, usuario_id: str) -> bool:
    """
    Elimina un usuario por su ID de la base de datos.
    """
    try:
        result = await db.usuarios.delete_one({"_id": ObjectId(usuario_id)})
        print(f"DEBUG (Controller): Usuario eliminado ({usuario_id}): {result.deleted_count > 0}")
        return result.deleted_count > 0
    except Exception as e:
        print(f"ERROR (Controller): Error al eliminar usuario '{usuario_id}': {e}")
        return False

# --- Funciones de Progreso ---

async def get_ultimo_peso_por_ejercicio(db: AsyncIOMotorDatabase, usuario_id: str) -> List[Dict[str, Any]]:
    """
    Obtiene el último peso registrado por ejercicio para un usuario.
    """
    try:
        pipeline = [
            {"$match": {"usuario_id": usuario_id}},
            {"$sort": {"fecha_registro": -1}},
            {"$group": {
                "_id": "$ejercicio_nombre",
                "ultimo_peso": {"$first": "$peso_levantado"},
                "ultimas_repeticiones": {"$first": "$repeticiones"},
                "ultima_fecha": {"$first": "$fecha_registro"}
            }},
            {"$project": {
                "ejercicio_nombre": "$_id",
                "ultimo_peso": 1,
                "ultimas_repeticiones": 1,
                "ultima_fecha": 1,
                "_id": 0 # Excluir el _id del grupo para este caso específico si no lo necesitas
            }}
        ]
        result = await db.registros.aggregate(pipeline).to_list(None)
        # Convertir cualquier ObjectId residual en el resultado de la agregación
        processed_result = _convert_id_to_str(result)
        print(f"DEBUG (Controller): Último peso por ejercicio para {usuario_id}: {processed_result}")
        return processed_result
    except Exception as e:
        print(f"ERROR (Controller): Error al obtener último peso por ejercicio para {usuario_id}: {e}")
        return []

async def get_mejor_marca(db: AsyncIOMotorDatabase, usuario_id: str, ejercicio_nombre: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene la mejor marca (peso * repeticiones o solo peso) para un ejercicio específico de un usuario.
    """
    try:
        pipeline = [
            {"$match": {"usuario_id": usuario_id, "ejercicio_nombre": ejercicio_nombre}},
            {"$addFields": {"volumen": {"$multiply": ["$peso_levantado", "$repeticiones"]}}},
            {"$sort": {"volumen": -1, "peso_levantado": -1, "repeticiones": -1}},
            {"$limit": 1}
        ]
        result = await db.registros.aggregate(pipeline).to_list(None)
        if result:
            # Convertir cualquier ObjectId residual en el resultado de la agregación
            processed_result = _convert_id_to_str(result[0])
            print(f"DEBUG (Controller): Mejor marca para {usuario_id} - {ejercicio_nombre}: {processed_result}")
            return processed_result
        print(f"DEBUG (Controller): No se encontró mejor marca para {usuario_id} - {ejercicio_nombre}")
        return None
    except Exception as e:
        print(f"ERROR (Controller): Error al obtener mejor marca para {usuario_id} - {ejercicio_nombre}: {e}")
        return None

async def get_frecuencia_semanal(db: AsyncIOMotorDatabase, usuario_id: str) -> List[Dict[str, Any]]:
    """
    Calcula la frecuencia semanal de registros para un usuario.
    """
    try:
        pipeline = [
            {"$match": {"usuario_id": usuario_id}},
            {"$group": {
                "_id": {
                    "año": {"$year": "$fecha_registro"},
                    "semana": {"$week": "$fecha_registro"}
                },
                "dias": {"$addToSet": {"$dayOfWeek": "$fecha_registro"}},
                "conteo": {"$sum": 1}
            }},
            {"$project": {
                "año": "$_id.año",
                "semana": "$_id.semana",
                "dias": {"$size": "$dias"},
                "conteo_registros": "$conteo",
                "_id": 0
            }},
            {"$sort": {"año": 1, "semana": 1}}
        ]
        result = await db.registros.aggregate(pipeline).to_list(None)
        # Convertir cualquier ObjectId residual en el resultado de la agregación (si _id del grupo fuera ObjectId, etc.)
        processed_result = _convert_id_to_str(result)
        print(f"DEBUG (Controller): Frecuencia semanal para {usuario_id}: {processed_result}")
        return processed_result
    except Exception as e:
        print(f"ERROR (Controller): Error al obtener frecuencia semanal para {usuario_id}: {e}")
        return []


async def get_volumen_total(db: AsyncIOMotorDatabase, usuario_id: str) -> float:
    """
    Calcula el volumen total de levantamiento para un usuario.
    """
    try:
        pipeline = [
            {"$match": {"usuario_id": usuario_id}},
            {"$group": {
                "_id": None,
                "volumen_total": {"$sum": {"$multiply": ["$peso_levantado", "$repeticiones"]}}
            }}
        ]
        result = await db.registros.aggregate(pipeline).to_list(None)
        # La agregación aquí es simple y debería devolver un número, no un ObjectId.
        volumen = result[0]["volumen_total"] if result else 0.0
        print(f"DEBUG (Controller): Volumen total para {usuario_id}: {volumen}")
        return volumen
    except Exception as e:
        print(f"ERROR (Controller): Error al obtener volumen total para {usuario_id}: {e}")
        return 0.0
