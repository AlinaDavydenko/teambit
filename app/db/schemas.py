from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime

# *** USER REGISTER - LOGIN ***


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


# *** BOARDS ***


class BoardCreate(BaseModel):
    """Data that comes to us while creating"""

    name: str
    color: str = "F5EEDF"


class BoardResponse(BaseModel):
    """Response"""

    model_config = ConfigDict(from_attributes=True)

    board_id: int
    name: str
    color: str
    user_id: int
    created_at: datetime


# *** Members ***


class AddMember(BaseModel):
    user_id: int
