from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RegistroBase(BaseModel):
    usuario_id: str
    ejercicio_id: Optional[str]
    ejercicio_nombre: str
    peso_levantado: float
    repeticiones: int
    fecha_registro: datetime
    notas: Optional[str] = None