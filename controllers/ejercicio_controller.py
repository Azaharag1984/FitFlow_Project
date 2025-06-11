from bson import ObjectId
from fastapi import HTTPException
from models.ejercicio import ejercicios_collection

def get_ejercicio_by_id(ejercicio_id: str):
    """
    Obtiene un ejercicio por su ID.
    """
    if not ObjectId.is_valid(ejercicio_id):
        raise HTTPException(status_code=400, detail="ID de ejercicio inválido")

    ejercicio = ejercicios_collection.find_one({"_id": ObjectId(ejercicio_id)})
    
    if not ejercicio:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    
    return ejercicio


def get_all_ejercicios():
    """
    Obtiene todos los ejercicios.
    """
    ejercicios = list(ejercicios_collection.find())
    
    if not ejercicios:
        raise HTTPException(status_code=404, detail="No se encontraron ejercicios")
    
    return ejercicios


def create_ejercicio(ejercicio_data: dict):
    """
    Crea un nuevo ejercicio.
    """
    if not ejercicio_data.get("nombre") or not ejercicio_data.get("descripcion"):
        raise HTTPException(status_code=400, detail="Datos de ejercicio incompletos")
    
    result = ejercicios_collection.insert_one(ejercicio_data)
    
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Error al crear el ejercicio")
    
    return str(result.inserted_id)


def update_ejercicio(ejercicio_id: str, ejercicio_data: dict):
    """
    Actualiza un ejercicio existente.
    """  
    if not ObjectId.is_valid(ejercicio_id):
        raise HTTPException(status_code=400, detail="ID de ejercicio inválido")

    if not ejercicio_data:
        raise HTTPException(status_code=400, detail="Datos de ejercicio incompletos")

    result = ejercicios_collection.update_one(
        {"_id": ObjectId(ejercicio_id)},
        {"$set": ejercicio_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado o no se realizaron cambios")
    
    return str(ejercicio_id)  # Retorna el ID del ejercicio actualizado


def delete_ejercicio(ejercicio_id: str):
    """
    Elimina un ejercicio por su ID.
    """ 
    if not ObjectId.is_valid(ejercicio_id):
        raise HTTPException(status_code=400, detail="ID de ejercicio inválido")

    result = ejercicios_collection.delete_one({"_id": ObjectId(ejercicio_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    
    return {"message": "Ejercicio eliminado exitosamente"}


def get_ejercicios_by_usuario(usuario_id: str):
    """
    Obtiene todos los ejercicios asociados a un usuario.
    """
    if not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    ejercicios = list(ejercicios_collection.find({"usuario_id": ObjectId(usuario_id)}))
    
    if not ejercicios:
        raise HTTPException(status_code=404, detail="No se encontraron ejercicios para el usuario")
    
    return ejercicios


def get_ejercicios_by_conversacion(conversacion_id: str):
    """
    Obtiene todos los ejercicios asociados a una conversación.
    """
    if not ObjectId.is_valid(conversacion_id):
        raise HTTPException(status_code=400, detail="ID de conversación inválido")

    ejercicios = list(ejercicios_collection.find({"conversacion_id": ObjectId(conversacion_id)}))
    
    if not ejercicios:
        raise HTTPException(status_code=404, detail="No se encontraron ejercicios para la conversación")
    
    return ejercicios