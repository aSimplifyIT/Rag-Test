from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    password: str
    confirm_password: str
    email: str