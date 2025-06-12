# Este archivo contendrá el código necesario para completar FitFlow más allá de los CRUD
# Incluiré funcionalidades específicas para controllers y rutas adicionales, como progreso, estadísticas y chatbot

# controllers/registro_controller.py (funciones adicionales)
from .app.connection.database import db
from bson import ObjectId
from datetime import datetime
from pymongo import DESCENDING

async def get_historial_por_ejercicio(usuario_id, ejercicio_nombre):
    registros = await db.registros.find({
        "usuario_id": ObjectId(usuario_id),
        "ejercicio_nombre": ejercicio_nombre
    }).sort("fecha_registro", 1).to_list(length=100)
    return registros

async def get_ultimo_peso_por_ejercicio(usuario_id):
    pipeline = [
        {"$match": {"usuario_id": ObjectId(usuario_id)}},
        {"$sort": {"fecha_registro": -1}},
        {"$group": {
            "_id": "$ejercicio_nombre",
            "ultimo_peso": {"$first": "$peso_levantado"},
            "fecha": {"$first": "$fecha_registro"}
        }}
    ]
    return await db.registros.aggregate(pipeline).to_list(length=100)

async def get_mejor_marca(usuario_id, ejercicio_nombre):
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

async def get_frecuencia_semanal(usuario_id):
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

async def get_volumen_total(usuario_id):
    pipeline = [
        {"$match": {"usuario_id": ObjectId(usuario_id)}},
        {"$project": {
            "volumen": {"$multiply": ["$peso_levantado", "$repeticiones"]}
        }},
        {"$group": {"_id": None, "volumen_total": {"$sum": "$volumen"}}}
    ]
    result = await db.registros.aggregate(pipeline).to_list(1)
    return result[0]["volumen_total"] if result else 0

# routes/usuarios.py (nuevas rutas para dashboard)
from fastapi import APIRouter
from controllers import registro_controller

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/{user_id}/progreso")
async def progreso_usuario(user_id: str):
    ultimo_peso = await registro_controller.get_ultimo_peso_por_ejercicio(user_id)
    return {"ultimo_peso": ultimo_peso}

@router.get("/{user_id}/progreso/{ejercicio}")
async def progreso_por_ejercicio(user_id: str, ejercicio: str):
    historial = await registro_controller.get_historial_por_ejercicio(user_id, ejercicio)
    mejor = await registro_controller.get_mejor_marca(user_id, ejercicio)
    return {"historial": historial, "mejor_marca": mejor}

@router.get("/{user_id}/estadisticas")
async def estadisticas_generales(user_id: str):
    frecuencia = await registro_controller.get_frecuencia_semanal(user_id)
    volumen = await registro_controller.get_volumen_total(user_id)
    return {"frecuencia_semanal": frecuencia, "volumen_total": volumen}
