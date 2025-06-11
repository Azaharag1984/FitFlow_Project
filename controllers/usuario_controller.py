from bson import ObjectId
from fastapi import HTTPException
from models.usuario import usuarios_collection

def get_usuario_by_id(usuario_id: str):
    """
    Obtiene un usuario por su ID.
    """
    if not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return usuario


def get_all_usuarios():
    """
    Obtiene todos los usuarios.
    """
    usuarios = list(usuarios_collection.find())
    
    if not usuarios:
        raise HTTPException(status_code=404, detail="No se encontraron usuarios")
    
    return usuarios


def create_usuario(usuario_data: dict):
    """
    Crea un nuevo usuario.
    """
    if not usuario_data.get("nombre") or not usuario_data.get("email"):
        raise HTTPException(status_code=400, detail="Datos de usuario incompletos")
    
    result = usuarios_collection.insert_one(usuario_data)
    
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Error al crear el usuario")
    
    return str(result.inserted_id)


def update_usuario(usuario_id: str, usuario_data: dict):
    """
    Actualiza un usuario existente.
    """
    if not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    if not usuario_data:
        raise HTTPException(status_code=400, detail="Datos de usuario incompletos")

    result = usuarios_collection.update_one(
        {"_id": ObjectId(usuario_id)},
        {"$set": usuario_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"message": "Usuario actualizado exitosamente"}


def delete_usuario(usuario_id: str):
    """
    Elimina un usuario por su ID.
    """
    if not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    result = usuarios_collection.delete_one({"_id": ObjectId(usuario_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"message": "Usuario eliminado exitosamente"}

