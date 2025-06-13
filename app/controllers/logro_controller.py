from bson import ObjectId
from fastapi import HTTPException
from models.logro import logros_collection

def get_logro_by_id(logro_id: str):
    try:
        # Verifica si el ID es válido
        if not ObjectId.is_valid(logro_id):
            raise HTTPException(status_code=400, detail="ID de logro inválido")
        
        # Busca el logro
        logro = logros_collection.find_one({"_id": ObjectId(logro_id)})
        if logro is None:
            raise HTTPException(status_code=404, detail="Logro no encontrado")
        
        return logro
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar el logro.")


def get_all_logros():
    try:
        # Recupera todos los logros
        logros = list(logros_collection.find())
        if not logros:
            raise HTTPException(status_code=404, detail="No se encontraron logros")
        
        return logros
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar los logros.")


def create_logro(logro_data: dict):
    try:
        # Valida los campos requeridos
        if not logro_data.get("nombre") or not logro_data.get("descripcion"):
            raise HTTPException(status_code=400, detail="Datos de logro incompletos")
        
        # Inserta el nuevo logro
        result = logros_collection.insert_one(logro_data)
        
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Error al crear el logro")
        
        return str(result.inserted_id)
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al crear el logro.")


def update_logro(logro_id: str, logro_data: dict):
    try:
        # Verifica si el ID es válido
        if not ObjectId.is_valid(logro_id):
            raise HTTPException(status_code=400, detail="ID de logro inválido")

        # Actualiza el logro
        result = logros_collection.update_one(
            {"_id": ObjectId(logro_id)},
            {"$set": logro_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Logro no encontrado o no se realizaron cambios")
        
        return str(logro_id)
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al actualizar el logro.")


def delete_logro(logro_id: str):
    try:
        # Verifica si el ID es válido
        if not ObjectId.is_valid(logro_id):
            raise HTTPException(status_code=400, detail="ID de logro inválido")

        # Elimina el logro
        result = logros_collection.delete_one({"_id": ObjectId(logro_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Logro no encontrado")
        
        return str({"detail": "Logro eliminado exitosamente"})
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al eliminar el logro.")


def get_logros_by_usuario(usuario_id: str):
    try:
        # Verifica si el ID de usuario es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")

        # Busca los logros del usuario
        logros = list(logros_collection.find({"usuario_id": ObjectId(usuario_id)}))
        
        if not logros:
            raise HTTPException(status_code=404, detail="No se encontraron logros para el usuario")
        
        return logros
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar los logros del usuario.")


def add_logro_to_usuario(usuario_id: str, logro_id: str):
    try:
        # Verifica si el ID de usuario es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Verifica si el ID de logro es válido
        if not ObjectId.is_valid(logro_id):
            raise HTTPException(status_code=400, detail="ID de logro inválido")
        
        # Actualiza el usuario para agregar el logro
        result = logros_collection.update_one(
            {"_id": ObjectId(logro_id)},
            {"$addToSet": {"usuarios": ObjectId(usuario_id)}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Logro no encontrado o ya agregado al usuario")
        
        return {"detail": "Logro agregado al usuario exitosamente"}
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al agregar el logro al usuario.")


def get_logros_tipo(usuario_id, tipo):
    try:
        # Verifica si el ID de usuario es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Busca los logros del usuario por tipo
        logros = list(logros_collection.find({"usuario_id": ObjectId(usuario_id), "tipo": tipo}))
        
        if not logros:
            raise HTTPException(status_code=404, detail="No se encontraron logros del tipo especificado para el usuario")
        
        return logros
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar los logros del tipo especificado del usuario.")
