from bson import ObjectId
from fastapi import HTTPException
from models.registro import registros_collection
from connection.database import db
from datetime import datetime
from pymongo import DESCENDING

def get_registro_by_id(registro_id: str):
    try:
        # Verifica si el ID es válido
        if not ObjectId.is_valid(registro_id):
            raise HTTPException(status_code=400, detail="ID de registro inválido")
        
        # Busca el registro
        registro = registros_collection.find_one({"_id": ObjectId(registro_id)})
        if registro is None:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        
        return registro
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar el registro.")


def get_all_registros():
    try:
        # Recupera todos los registros
        registros = list(registros_collection.find())
        if not registros:
            raise HTTPException(status_code=404, detail="No se encontraron registros")
        
        return registros
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar los registros.")


def create_registro(registro_data: dict):
    try:
        # Valida los campos requeridos
        if not registro_data.get("usuario_id") or not registro_data.get("fecha"):
            raise HTTPException(status_code=400, detail="Datos de registro incompletos")
        
        # Inserta el nuevo registro
        result = registros_collection.insert_one(registro_data)
        
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Error al crear el registro")
        
        return str(result.inserted_id)
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al crear el registro.")


def update_registro(registro_id: str, registro_data: dict):
    try:
        # Verifica si el ID es válido
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
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al actualizar el registro.")


def delete_registro(registro_id: str):
    try:
        # Verifica si el ID es válido
        if not ObjectId.is_valid(registro_id):
            raise HTTPException(status_code=400, detail="ID de registro inválido")

        result = registros_collection.delete_one({"_id": ObjectId(registro_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        
        return {"detail": "Registro eliminado exitosamente"}
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al eliminar el registro.")


def get_registros_by_usuario(usuario_id: str):
    try:
        # Verifica si el ID de usuario es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")

        # Recupera los registros del usuario
        registros = list(registros_collection.find({"usuario_id": ObjectId(usuario_id)}))
        
        if not registros:
            raise HTTPException(status_code=404, detail="No se encontraron registros para el usuario")
        
        return registros
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar los registros del usuario.")


async def get_historial_por_ejercicio(usuario_id, ejercicio_nombre):
    try:
        # Verifica si el ID de usuario es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")

        # Busca los registros del usuario por ejercicio
        registros = list(registros_collection.find({
            "usuario_id": ObjectId(usuario_id),
            "ejercicio_nombre": ejercicio_nombre
        }))

        if not registros:
            raise HTTPException(status_code=404, detail="No se encontraron registros para el ejercicio")

        return registros
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar el historial del ejercicio.")


async def get_registros_por_fecha(usuario_id, fecha_inicio, fecha_fin):
    try:
        # Verifica si el ID de usuario es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Convierte las fechas a objetos datetime
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

        # Busca los registros dentro del rango de fechas
        registros = list(registros_collection.find({
            "usuario_id": ObjectId(usuario_id),
            "fecha_registro": {
                "$gte": fecha_inicio,
                "$lte": fecha_fin
            }
        }).sort("fecha_registro", DESCENDING))

        if not registros:
            raise HTTPException(status_code=404, detail="No se encontraron registros en el rango de fechas especificado")
        
        return registros
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar los registros por fecha.")