from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime


class UserRegister(BaseModel):
    """Data that user sends us upon registration"""

    first_name: str
    last_name: str
    nickname: str
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    """Data that user sends us upon log in"""

    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    """Server returns us (without a password)"""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    first_name: str
    last_name: str
    nickname: str
    email: EmailStr
    created_at: datetime
