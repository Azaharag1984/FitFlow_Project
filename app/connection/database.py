from motor.motor_asyncio import AsyncIOMotorClient # ¡Cambio clave aquí!
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

class Database:
    client: Optional[AsyncIOMotorClient] = None # Tipo de cliente actualizado

async def connect_to_mongo(): # ¡Ahora es una función asíncrona!
    try:
        Database.client = AsyncIOMotorClient(MONGO_URI) # ¡Cambio clave aquí!
        db = Database.client[DB_NAME]
        print(f"Conectado a la base de datos {DB_NAME} en {MONGO_URI}")
        return db
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise e

async def close_mongo_connection(): # ¡Ahora es una función asíncrona!
    if Database.client:
        Database.client.close()
        print("Conexión a la base de datos cerrada.")

