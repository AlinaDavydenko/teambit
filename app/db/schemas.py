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


class BoardMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    nickname: str
    email: EmailStr
    role: str


class BoardColorUpdate(BaseModel):
    color: str


# *** MEMBERS ***


class AddMember(BaseModel):
    user_id: int


# *** COLUMNS ***


class ColumnCreate(BaseModel):
    name: str


class ColumnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    column_id: int
    board_id: int
    name: str
    position: int


class ColumnUpdate(BaseModel):
    name: str


# *** CARDS ***


class CardCreate(BaseModel):
    name: str
    color: str = "F7F2FC"
    task_description: str | None = None
    priority: int | None = None
    deadline: datetime | None = None
    tags: str | None = None


class CardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    color: str
    task_description: str | None = None
    column_id: int
    position: int
    priority: int | None = None
    tags: str | None = None
    deadline: datetime | None = None
    is_template: bool


class CardUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    task_description: str | None = None
    priority: int | None = None
    deadline: datetime | None = None
    tags: str | None = None


class CardMove(BaseModel):
    column_id: int
    position: int
