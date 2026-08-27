from typing import Literal

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.enums import TicketPriority, TicketStatus, UserRole

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


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assigned_to_id: int | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes":True}

class CategoryCreate(BaseModel):
    name: str = Field(min_length=5, max_length=200)




class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)



class CommentResponse(BaseModel):
    id: int
    content: str
    ticket_id: int
    author_id: int
    created_at: datetime

    model_config={
        "from_attributes":True
    }


class TicketAssign(BaseModel):
    agent_id: int


class TicketListResponse(BaseModel):
    items: list [TicketResponse]
    total: int
    page: int
    limit: int
    pages: int


class UserRoleUpdate(BaseModel):
    role: Literal[UserRole.AGENT, UserRole.CUSTOMER]