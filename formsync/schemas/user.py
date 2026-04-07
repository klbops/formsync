from pydantic import BaseModel, EmailStr
from typing import Optional

# Molde para criar um novo usuário
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

# Molde para retornar os dados do usuário (sem a senha!)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        from_attributes = True

# Molde para o Token de Login
class Token(BaseModel):
    access_token: str
    token_type: str
