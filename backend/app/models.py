from sqlalchemy import Boolean, Index, String, ForeignKey, Text, DateTime
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
    __table_args__ = (
        Index("ix_tickets_status", "status"),
        Index("ix_tickets_priority", "priority"),
        Index("ix_tickets_created_by", "created_by_id"),
        Index("ix_tickets_assigned_to", "assigned_to_id"),
        Index("ix_tickets_category", "category_id"),
        Index("ix_tickets_assigned_status", "assigned_to_id", "status"),
        Index("ix_tickets_creator_status", "created_by_id", "status"),
    )

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
    closed_by_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)

    creator: Mapped["User"] = relationship(foreign_keys=[created_by_id])
    assignee: Mapped["User | None"] = relationship(foreign_keys=[assigned_to_id])
    closed_by: Mapped["User | None"] = relationship(foreign_keys=[closed_by_id])
    category: Mapped["Category"] = relationship()

    @property
    def created_by(self) -> "User":
        return self.creator

    @property
    def assigned_to(self) -> "User | None":
        return self.assignee




class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    ticketr_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False, index=True)
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

    @property
    def user_id(self) -> int:
        return self.author_id

    @property
    def user(self) -> "User":
        return self.author


class TicketActivity(Base):
    __tablename__ = "ticket_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[str | None] =  mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(), nullable=False)
    ticket: Mapped["Ticket"] = relationship()
    user: Mapped["User"] = relationship()