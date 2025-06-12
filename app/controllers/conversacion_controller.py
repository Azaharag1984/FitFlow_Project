from bson import ObjectId
from fastapi import HTTPException
from models.conversacion import conversaciones_collection


def get_conversacion_by_id(conversacion_id: str):
    try:
        # Check if the ID is valid
        if not ObjectId.is_valid(conversacion_id):
            raise HTTPException(status_code=400, detail="ID de conversación inválido")
        
        # Search for the conversacion
        conversacion = conversaciones_collection.find_one({"_id": ObjectId(conversacion_id)})
        if conversacion is None:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        return conversacion
    except HTTPException as e:
        raise e  # Re-raise the custom exception
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar la conversación.")


def get_all_conversaciones():
    try:
        # Retrieve all conversations
        conversaciones = list(conversaciones_collection.find())
        if not conversaciones:
            raise HTTPException(status_code=404, detail="No se encontraron conversaciones")
        
        return conversaciones
    except HTTPException as e:
        raise e  # Re-raise the custom exception
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar las conversaciones.")


def create_conversacion(conversacion_data: dict):
    try:
        # Validate required fields
        if not conversacion_data.get("usuario_id") or not conversacion_data.get("mensaje"):
            raise HTTPException(status_code=400, detail="Datos de conversación incompletos")
        
        # Insert the new conversation
        result = conversaciones_collection.insert_one(conversacion_data)
        
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Error al crear la conversación")
        
        return str(result.inserted_id)
    except HTTPException as e:
        raise e # Re-raise the custom exception
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al crear la conversación.")


def update_conversacion(conversacion_id: str, conversacion_data: dict):
    try:
        # Validate the conversation ID
        if not ObjectId.is_valid(conversacion_id):
            raise HTTPException(status_code=400, detail="ID de conversación inválido")
        
        # Validate required fields
        if not conversacion_data:
            raise HTTPException(status_code=400, detail="Datos de conversación incompletos")
        
        # Update the conversation
        result = conversaciones_collection.update_one(
            {"_id": ObjectId(conversacion_id)},
            {"$set": conversacion_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Conversación no encontrada o no se realizaron cambios")
        
        return str(conversacion_id)
    except HTTPException as e:
        raise e  # Re-raise the custom exception
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al actualizar la conversación.")


def delete_conversacion(conversacion_id: str):
    try:
        # Check if the ID is valid
        if not ObjectId.is_valid(conversacion_id):
            raise HTTPException(status_code=400, detail="Invalid conversacion ID")
        
        result = conversaciones_collection.delete_one({"_id": ObjectId(conversacion_id)})
        if result.deleted_count > 0:
            return True
        raise HTTPException(status_code=404, detail="conversacion not found")
    except HTTPException as e:
        raise e  # Re-raise the custom exception
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error deleting the conversacion")


def get_conversaciones_by_usuario(usuario_id: str):
    try:
        # Check if the user ID is valid
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Retrieve conversations for the user
        conversaciones = list(conversaciones_collection.find({"usuario_id": ObjectId(usuario_id)}))
        
        if not conversaciones:
            raise HTTPException(status_code=404, detail="No se encontraron conversaciones para este usuario")
        
        return conversaciones
    except HTTPException as e:
        raise e # Re-raise the custom exception
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar las conversaciones del usuario.")


def get_ultimos_mensajes(usuario_id, n):
    try:
        # Check if the user ID is valid
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Retrieve the last n messages for the user
        mensajes = list(conversaciones_collection.find({"usuario_id": ObjectId(usuario_id)}).sort("fecha", -1).limit(n))
        
        if not mensajes:
            raise HTTPException(status_code=404, detail="No se encontraron mensajes recientes para este usuario")
        
        return mensajes
    except HTTPException as e:
        raise e  # Re-raise the custom exception
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar los últimos mensajes del usuario.")


def get_mensajes_por_tema(usuario_id, tema):
    try:
        # Check if the user ID is valid
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Retrieve messages related to a specific topic for the user
        mensajes = list(conversaciones_collection.find({
            "usuario_id": ObjectId(usuario_id),
            "tema": tema
        }))
        
        if not mensajes:
            raise HTTPException(status_code=404, detail="No se encontraron mensajes para este tema")
        
        return mensajes
    except HTTPException as e:
        raise e  # Re-raise the custom exception
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar los mensajes por tema.")


def analizar_estado_animo(usuario_id):
    try:
        # Check if the user ID is valid
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Retrieve conversations for the user
        conversaciones = list(conversaciones_collection.find({"usuario_id": ObjectId(usuario_id)}))
        
        if not conversaciones:
            raise HTTPException(status_code=404, detail="No se encontraron conversaciones para este usuario")
        
        # Analyze the mood based on the messages (this is a placeholder for actual analysis logic)
        estado_animo = "Neutral"  # Placeholder logic
        
        return {"estado_animo": estado_animo}
    except HTTPException as e:
        raise e  # Re-raise the custom exception
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al analizar el estado de ánimo del usuario.")

