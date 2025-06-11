from bson import ObjectId
from fastapi import HTTPException
from models.registro import registros_collection

def get_registro_by_id(registro_id: str):
    """
    Obtiene un registro por su ID.
    """
    if not ObjectId.is_valid(registro_id):
        raise HTTPException(status_code=400, detail="ID de registro inválido")

    registro = registros_collection.find_one({"_id": ObjectId(registro_id)})
    
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    
    return registro


def get_all_registros():
    """
    Obtiene todos los registros.
    """
    registros = list(registros_collection.find())
    
    if not registros:
        raise HTTPException(status_code=404, detail="No se encontraron registros")
    
    return registros


def create_registro(registro_data: dict):
    """
    Crea un nuevo registro.
    """
    if not registro_data.get("usuario_id") or not registro_data.get("fecha"):
        raise HTTPException(status_code=400, detail="Datos de registro incompletos")
    
    result = registros_collection.insert_one(registro_data)
    
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Error al crear el registro")
    
    return str(result.inserted_id)


def update_registro(registro_id: str, registro_data: dict):
    """
    Actualiza un registro existente.
    """
    if not ObjectId.is_valid(registro_id):
        raise HTTPException(status_code=400, detail="ID de registro inválido")

    if not registro_data:
        raise HTTPException(status_code=400, detail="Datos de registro incompletos")

    result = registros_collection.update_one(
        {"_id": ObjectId(registro_id)},
        {"$set": registro_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Registro no encontrado o no se realizaron cambios")
    
    return str(registro_id)


def delete_registro(registro_id: str):
    """
    Elimina un registro por su ID.
    """
    if not ObjectId.is_valid(registro_id):
        raise HTTPException(status_code=400, detail="ID de registro inválido")

    result = registros_collection.delete_one({"_id": ObjectId(registro_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    
    return {"detail": "Registro eliminado exitosamente"}


def get_registros_by_usuario(usuario_id: str):
    """
    Obtiene todos los registros de un usuario específico.
    """
    if not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    registros = list(registros_collection.find({"usuario_id": ObjectId(usuario_id)}))
    
    if not registros:
        raise HTTPException(status_code=404, detail="No se encontraron registros para el usuario")
    
    return registros
#