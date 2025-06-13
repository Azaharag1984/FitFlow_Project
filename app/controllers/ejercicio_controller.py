from bson import ObjectId
from fastapi import HTTPException
from models.ejercicio import ejercicios_collection

def get_ejercicio_by_id(ejercicio_id: str):
    try:
        # Verifica si el ID es válido
        if not ObjectId.is_valid(ejercicio_id):
            raise HTTPException(status_code=400, detail="ID de ejercicio inválido")
        
        # Busca el ejercicio
        ejercicio = ejercicios_collection.find_one({"_id": ObjectId(ejercicio_id)})
        if ejercicio is None:
            raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
        
        return ejercicio
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar el ejercicio.")


def get_all_ejercicios():
    try:
        # Recupera todos los ejercicios
        ejercicios = list(ejercicios_collection.find())
        if not ejercicios:
            raise HTTPException(status_code=404, detail="No se encontraron ejercicios")
        
        return ejercicios
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar los ejercicios.")


def create_ejercicio(ejercicio_data: dict):
    try:
        # Valida los campos requeridos
        if not ejercicio_data.get("nombre") or not ejercicio_data.get("descripcion"):
            raise HTTPException(status_code=400, detail="Datos de ejercicio incompletos")
        
        # Inserta el nuevo ejercicio
        result = ejercicios_collection.insert_one(ejercicio_data)
        
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Error al crear el ejercicio")
        
        return str(result.inserted_id)
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al crear el ejercicio.")


def update_ejercicio(ejercicio_id: str, ejercicio_data: dict):
    try:
        # Verifica si el ID es válido
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
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al actualizar el ejercicio.")


def delete_ejercicio(ejercicio_id: str):
    try:
        # Verifica si el ID es válido
        if not ObjectId.is_valid(ejercicio_id):
            raise HTTPException(status_code=400, detail="ID de ejercicio inválido")

        result = ejercicios_collection.delete_one({"_id": ObjectId(ejercicio_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
        
        return str({"message": "Ejercicio eliminado exitosamente"})
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al eliminar el ejercicio.")


def get_ejercicios_by_usuario(usuario_id: str):
    try:
        # Verifica si el ID de usuario es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")

        # Busca los ejercicios asociados al usuario
        ejercicios = list(ejercicios_collection.find({"usuario_id": ObjectId(usuario_id)}))
        
        if not ejercicios:
            raise HTTPException(status_code=404, detail="No se encontraron ejercicios para el usuario")
        
        return ejercicios
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar los ejercicios del usuario.")


def get_ejercicios_by_conversacion(conversacion_id: str):
    try:
        # Verifica si el ID de conversación es válido
        if not ObjectId.is_valid(conversacion_id):
            raise HTTPException(status_code=400, detail="ID de conversación inválido")
        # Busca los ejercicios asociados a la conversación
        ejercicios = list(ejercicios_collection.find({"conversacion_id": ObjectId(conversacion_id)}))
        if not ejercicios:
            raise HTTPException(status_code=404, detail="No se encontraron ejercicios para la conversación")
        return ejercicios
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar los ejercicios de la conversación.")

