from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")


class Database:
    client = None

def connect_to_mongo():
    try:
        Database.client = MongoClient(MONGO_URI)
        db = Database.client[DB_NAME]
        print(f"Conectado a la base de datos {DB_NAME} en {MONGO_URI}")
        return db
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise e

def close_mongo_connection():
    if Database.client:
        Database.client.close()
        print("Conexión a la base de datos cerrada.")