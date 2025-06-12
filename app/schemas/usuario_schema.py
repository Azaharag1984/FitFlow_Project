from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UsuariosSchema(BaseModel):
    nombre: str
    email: EmailStr
    objetivo: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        orm_mode = True

