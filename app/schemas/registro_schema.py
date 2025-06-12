from pydantic import BaseModel

class RegistrosSchema(BaseModel):
    name: str
    effect: str

    class Config:
        orm_mode = True