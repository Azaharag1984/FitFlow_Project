from bson import ObjectId
from fastapi import HTTPException
from models.usuario import usuarios_collection
# from connection.database import db
from datetime import datetime
from pymongo import DESCENDING

def get_usuario_by_id(usuario_id: str):
    try:
        # Verifica si el ID es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Busca el usuario
        usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})
        if usuario is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return usuario
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar el usuario.")


def get_all_usuarios():
    try:
        # Recupera todos los usuarios
        usuarios = list(usuarios_collection.find())
        
        if not usuarios:
            raise HTTPException(status_code=404, detail="No se encontraron usuarios")
        
        return usuarios  # Retorna la lista de usuarios

    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar los usuarios.")


def create_usuario(usuario_data: dict):
    try:
        # Valida los campos requeridos
        if not usuario_data.get("nombre") or not usuario_data.get("email"):
            raise HTTPException(status_code=400, detail="Datos de usuario incompletos")
        
        # Inserta el nuevo usuario
        result = usuarios_collection.insert_one(usuario_data)
        
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Error al crear el usuario")
        
        return str(result.inserted_id)
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al crear el usuario.")


def update_usuario(usuario_id: str, usuario_data: dict):
    try:
        # Verifica si el ID es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")

        # Verifica que los datos no estén vacíos
        if not usuario_data:
            raise HTTPException(status_code=400, detail="Datos de usuario incompletos")

        result = usuarios_collection.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": usuario_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {"message": "Usuario actualizado exitosamente"}
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al actualizar el usuario.")


def delete_usuario(usuario_id: str):
    try:
        # Verifica si el ID es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")

        # Elimina el usuario
        result = usuarios_collection.delete_one({"_id": ObjectId(usuario_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {"message": "Usuario eliminado exitosamente"}
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al eliminar el usuario.")


async def get_ultimo_peso_por_ejercicio(usuario_id):
    try:
        # Verifica si el ID de usuario es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")

        # Define el pipeline de agregación
        pipeline = [
            {"$match": {"usuario_id": ObjectId(usuario_id)}},
            {"$sort": {"fecha_registro": -1}},
            {"$group": {
                "_id": "$ejercicio_nombre",
                "ultimo_peso": {"$first": "$peso_levantado"},
                "fecha": {"$first": "$fecha_registro"}
            }}
        ]

        # Ejecuta la agregación y retorna los resultados
        return await db.registros.aggregate(pipeline).to_list(length=100)
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar el último peso por ejercicio.")


async def get_mejor_marca(usuario_id, ejercicio_nombre):
    try:
        # Verifica si el ID de usuario es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        if not ejercicio_nombre:
            raise HTTPException(status_code=400, detail="Nombre del ejercicio es requerido")
        if not isinstance(ejercicio_nombre, str):
            raise HTTPException(status_code=400, detail="El nombre del ejercicio debe ser una cadena de texto")
        
        # Define el pipeline de agregación para obtener la mejor marca
        pipeline = [
            {"$match": {
                "usuario_id": ObjectId(usuario_id),
                "ejercicio_nombre": ejercicio_nombre
            }},
            {"$group": {
                "_id": "$ejercicio_nombre",
                "mejor_marca": {"$max": "$peso_levantado"}
            }}
        ]
        result = await db.registros.aggregate(pipeline).to_list(1)
        return result[0] if result else {}
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:  
        raise HTTPException(status_code=500, detail="Error al recuperar la mejor marca del ejercicio.")


async def get_frecuencia_semanal(usuario_id):
    try:
        # Verifica si el ID de usuario es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Define el pipeline de agregación para calcular la frecuencia semanal
        pipeline = [
            {"$match": {"usuario_id": ObjectId(usuario_id)}},
            {"$project": {
                "año": {"$year": "$fecha_registro"},
                "semana": {"$isoWeek": "$fecha_registro"}
            }},
            {"$group": {
                "_id": {"año": "$año", "semana": "$semana"},
                "dias": {"$sum": 1}
            }}
        ]
        return await db.registros.aggregate(pipeline).to_list(length=52)
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar la frecuencia semanal de ejercicios.")

async def get_volumen_total(usuario_id):
    try:
        # Verifica si el ID de usuario es válido
        if not ObjectId.is_valid(usuario_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Define el pipeline de agregación para calcular el volumen total
        pipeline = [
            {"$match": {"usuario_id": ObjectId(usuario_id)}},
            {"$project": {
                "volumen": {"$multiply": ["$peso_levantado", "$repeticiones"]}
            }},
            {"$group": {"_id": None, "volumen_total": {"$sum": "$volumen"}}}
        ]
        result = await db.registros.aggregate(pipeline).to_list(1)
        return result[0]["volumen_total"] if result else 0
    except HTTPException as e:
        raise e  # Re-lanza la excepción personalizada
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar el volumen total de ejercicios.")



