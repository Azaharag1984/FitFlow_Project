from bson import ObjectId
from fastapi import HTTPException
from models.conversacion import conversaciones_collection

def get_conversacion_by_id(conversacion_id: str):
    """
    Obtiene una conversación por su ID.
    """
    if not ObjectId.is_valid(conversacion_id):
        raise HTTPException(status_code=400, detail="ID de conversación inválido")

    conversacion = conversaciones_collection.find_one({"_id": ObjectId(conversacion_id)})
    
    if not conversacion:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    return conversacion


def get_all_conversaciones():
    """
    Obtiene todas las conversaciones.
    """
    conversaciones = list(conversaciones_collection.find())
    
    if not conversaciones:
        raise HTTPException(status_code=404, detail="No se encontraron conversaciones")
    
    return conversaciones


def create_conversacion(conversacion_data: dict):
    """
    Crea una nueva conversación.
    """             
    if not conversacion_data.get("usuario_id") or not conversacion_data.get("mensaje"):
        raise HTTPException(status_code=400, detail="Datos de conversación incompletos")
    
    result = conversaciones_collection.insert_one(conversacion_data)
    
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Error al crear la conversación")
    
    return str(result.inserted_id)


def update_conversacion(conversacion_id: str, conversacion_data: dict):
    """
    Actualiza una conversación existente.
    """
    if not ObjectId.is_valid(conversacion_id):
        raise HTTPException(status_code=400, detail="ID de conversación inválido")

    if not conversacion_data:
        raise HTTPException(status_code=400, detail="Datos de conversación incompletos")

    result = conversaciones_collection.update_one(
        {"_id": ObjectId(conversacion_id)},
        {"$set": conversacion_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Conversación no encontrada o no se realizaron cambios")
    
    return str(conversacion_id)


def delete_conversacion(conversacion_id: str):
    """
    Elimina una conversación por su ID.
    """
    if not ObjectId.is_valid(conversacion_id):
        raise HTTPException(status_code=400, detail="ID de conversación inválido")

    result = conversaciones_collection.delete_one({"_id": ObjectId(conversacion_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    return {"message": "Conversación eliminada exitosamente"}


def get_conversaciones_by_usuario(usuario_id: str):
    """
    Obtiene todas las conversaciones de un usuario específico.
    """
    if not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    conversaciones = list(conversaciones_collection.find({"usuario_id": ObjectId(usuario_id)}))
    
    if not conversaciones:
        raise HTTPException(status_code=404, detail="No se encontraron conversaciones para este usuario")
    
    return conversaciones


