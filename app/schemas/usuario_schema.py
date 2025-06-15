from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId
from pydantic_core import CoreSchema
from pydantic_core.core_schema import ValidationInfo

# Clase auxiliar para manejar la serialización de ObjectId de MongoDB en Pydantic V2
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any, info: ValidationInfo):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: Any
    ) -> CoreSchema:
        return handler(
            {
                "type": "string",
                "format": "objectid"
            }
        )

# --- MODELO DE ENTRADA (para crear o actualizar recursos) ---
# NO incluye el campo 'id'/'_id' porque MongoDB lo genera.
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    objetivo: Optional[str] = None
    # fecha_creacion no se debe enviar al crear; el backend la generará
    # o si se permite, debe ser opcional y el backend debe manejar si no se provee.

    class Config:
        populate_by_name = True # Renombrado de allow_population_by_field_name
        json_schema_extra = { # Ejemplo para la documentación OpenAPI
            "example": {
                "nombre": "Jane Doe",
                "email": "jane.doe@example.com",
                "objetivo": "Aprender FastAPI y MongoDB"
            }
        }

# --- MODELO DE SALIDA (para las respuestas de la API) ---
# SÍ incluye el campo 'id' que es el alias del '_id' de MongoDB.
class UsuarioResponse(BaseModel): # Renombremos tu UsuariosSchema a UsuarioResponse
    id: PyObjectId = Field(alias="_id") # Este campo es lo que Streamlit espera
    nombre: str
    email: EmailStr
    objetivo: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60c72b2f9f1b2c3d4e5f6a7b",
                "nombre": "Jane Doe",
                "email": "jane.doe@example.com",
                "objetivo": "Aprender FastAPI y MongoDB",
                "fecha_creacion": "2023-10-27T10:00:00Z"
            }
        }

