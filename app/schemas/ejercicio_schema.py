from pydantic import BaseModel, Field
from typing import Optional

class EjercicioBase(BaseModel):
    nombre: str
    grupo_muscular: Optional[str]
    descripcion: Optional[str]