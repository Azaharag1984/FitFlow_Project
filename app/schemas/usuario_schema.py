from pydantic import BaseModel

class UsuariosSchema(BaseModel):
    name: str
    effect: str

    class Config:
        orm_mode = True

