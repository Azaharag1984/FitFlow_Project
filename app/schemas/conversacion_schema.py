from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ConversacionBase(BaseModel):
    usuario_id: str
    fecha: datetime
    rol: str  # "user" o "assistant"
    mensaje: str
    tema: Optional[str]
