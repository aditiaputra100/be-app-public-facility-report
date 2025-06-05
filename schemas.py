from pydantic import BaseModel

class UserRegister(BaseModel):
    uid: str
    full_name: str