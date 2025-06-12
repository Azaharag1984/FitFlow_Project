from pydantic import BaseModel

class EjerciciosSchema(BaseModel):
    name: str
    effect: str

    class Config:
        orm_mode = True