from pydantic import BaseModel

class LogrosSchema(BaseModel):
    name: str
    effect: str

    class Config:
        orm_mode = True