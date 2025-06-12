from pydantic import BaseModel

class ConversacionesSchema(BaseModel):
    name: str
    effect: str

    class Config:
        orm_mode = True