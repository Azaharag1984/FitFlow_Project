from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId # Importante: Necesario para manejar ObjectId de MongoDB
from pydantic_core import CoreSchema
from pydantic_core.core_schema import ValidationInfo # ¡Nueva importación clave!

# Clase auxiliar para manejar la serialización de ObjectId de MongoDB en Pydantic V2
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any, info: ValidationInfo): # 'info' es el nuevo argumento
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: Any
    ) -> CoreSchema:
        # Aquí, le indicamos a Pydantic V2 que este tipo debe ser tratado como una cadena (string)
        # en el esquema JSON (lo que FastAPI usa para su documentación OpenAPI).
        return handler(
            {
                "type": "string",
                "format": "objectid" # Puedes añadir un formato para indicar que es un ObjectId
            }
        )

# --- MODELO DE ENTRADA (para crear o actualizar conversaciones) ---
# NO incluye el campo 'id'/'_id' porque MongoDB lo genera.
class ConversacionCreate(BaseModel):
    usuario_id: str
    fecha: datetime
    rol: str  # "user" o "assistant"
    mensaje: str
    tema: Optional[str] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "usuario_id": "60c72b2f9f1b2c3d4e5f6a7b",
                "fecha": "2023-11-05T09:00:00Z",
                "rol": "user",
                "mensaje": "¿Cuál es el mejor ejercicio para el pecho?",
                "tema": "entrenamiento"
            }
        }

# --- MODELO DE SALIDA (para las respuestas de la API) ---
# SÍ incluye el campo 'id' que es el alias del '_id' de MongoDB.
class ConversacionResponse(BaseModel):
    id: PyObjectId = Field(alias="_id") # Este campo es lo que Streamlit espera
    usuario_id: str
    fecha: datetime
    rol: str
    mensaje: str
    tema: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60c72b2f9f1b2c3d4e5f6a80",
                "usuario_id": "60c72b2f9f1b2c3d4e5f6a7b",
                "fecha": "2023-11-05T09:00:00Z",
                "rol": "user",
                "mensaje": "¿Cuál es el mejor ejercicio para el pecho?",
                "tema": "entrenamiento"
            }
        }
