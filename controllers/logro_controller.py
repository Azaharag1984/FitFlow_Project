from bson import ObjectId
from fastapi import HTTPException
from models.logro import logros_collection

def get_logro_by_id(logro_id: str):
    """
    Obtiene un logro por su ID.
    """
    if not ObjectId.is_valid(logro_id):
        raise HTTPException(status_code=400, detail="ID de logro inválido")

    logro = logros_collection.find_one({"_id": ObjectId(logro_id)})
    
    if not logro:
        raise HTTPException(status_code=404, detail="Logro no encontrado")
    
    return logro


def get_all_logros():
    """
    Obtiene todos los logros.
    """
    logros = list(logros_collection.find())
    
    if not logros:
        raise HTTPException(status_code=404, detail="No se encontraron logros")
    
    return logros


def create_logro(logro_data: dict):
    """
    Crea un nuevo logro.
    """
    if not logro_data.get("nombre") or not logro_data.get("descripcion"):
        raise HTTPException(status_code=400, detail="Datos de logro incompletos")
    
    result = logros_collection.insert_one(logro_data)
    
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Error al crear el logro")
    
    return str(result.inserted_id)


def update_logro(logro_id: str, logro_data: dict):
    """
    Actualiza un logro existente.
    """
    if not ObjectId.is_valid(logro_id):
        raise HTTPException(status_code=400, detail="ID de logro inválido")

    if not logro_data:
        raise HTTPException(status_code=400, detail="Datos de logro incompletos")

    result = logros_collection.update_one(
        {"_id": ObjectId(logro_id)},
        {"$set": logro_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Logro no encontrado o no se realizaron cambios")
    
    return str(logro_id)


def delete_logro(logro_id: str):
    """
    Elimina un logro por su ID.
    """
    if not ObjectId.is_valid(logro_id):
        raise HTTPException(status_code=400, detail="ID de logro inválido")

    result = logros_collection.delete_one({"_id": ObjectId(logro_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Logro no encontrado")
    
    return {"detail": "Logro eliminado exitosamente"}


def get_logros_by_usuario(usuario_id: str):
    """
    Obtiene todos los logros de un usuario específico.
    """
    if not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    logros = list(logros_collection.find({"usuario_id": ObjectId(usuario_id)}))
    
    if not logros:
        raise HTTPException(status_code=404, detail="No se encontraron logros para el usuario")
    
    return logros