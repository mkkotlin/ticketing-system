from sqlalchemy import Boolean, String, ForeignKey, Text, DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.enums import TicketPriority, TicketStatus

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="CUSTOMER", nullable=False)

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(default=TicketStatus.OPEN, nullable=False)
    priority: Mapped[TicketPriority] = mapped_column(default=TicketPriority.MEDIUM, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    creator: Mapped["User"] = relationship(foreign_keys=[created_by_id])
    assignee: Mapped["User | None"] = relationship(foreign_keys=[assigned_to_id])
    category: Mapped["Category"] = relationship()




class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    ticketr_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda:datetime.now(), nullable=False)
    ticket: Mapped["Ticket"] = relationship()
    author: Mapped["User"] = relationship()

    @property
    def ticket_id(self) -> int:
        return self.ticketr_id

    @ticket_id.setter
    def ticket_id(self, value: int):
        self.ticketr_id = value