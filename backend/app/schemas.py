from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.enums import TicketPriority, TicketStatus

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    model_config = { "from_attributes":True }

class Token(BaseModel):
    access_token: str
    token_type: str

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    category_id: int
    created_by_id: int
    assigned_to_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    resolved_at: datetime | None = None
    closed_by_id: int | None = None
        
    model_config = { "from_attributes": True }

class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    category_id: int
    priority: TicketPriority = TicketPriority.MEDIUM