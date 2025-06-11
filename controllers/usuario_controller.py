from database import db

async def crear_usuario(data):
    result = await db.usuarios.insert_one(data)
    return str(result.inserted_id)

async def obtener_usuarios():
    return await db.usuarios.find().to_list(100)
