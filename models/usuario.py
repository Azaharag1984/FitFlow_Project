from pydantic import BaseModel, Field
from typing import Optional, List

class Usuario(BaseModel):
    id: Optional[str] = Field(alias="_id")
    nombre: str
    email: str
    objetivo: Optional[str] = None
    lista_logros: Optional[List[str]] = []


