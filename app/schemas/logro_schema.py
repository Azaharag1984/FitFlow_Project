from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LogroBase(BaseModel):
    usuario_id: str
    ejercicio_id: Optional[str]
    descripcion: str
    valor: str
    fecha_logro: datetime
    tipo: Optional[str]
