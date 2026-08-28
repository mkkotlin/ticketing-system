from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..enums import UserRole

from ..database import get_db, get_transaction
from ..dependencies import get_current_user
from ..models import Comment, Ticket, User
from ..schemas import CommentCreate, CommentResponse
from app.services.activitiy_service import ActivityService
from app.exceptions import TicketNotFound, ForbiddenAction


router = APIRouter(
    prefix="/tickets/{ticket_id}/comments",
    tags=["Comments"]
)

@router.post("", response_model=CommentResponse, status_code=201)
def create_comment(ticket_id: int, comment_data: CommentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_transaction)):
    ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()

    if ticket is None:
        raise TicketNotFound()

    if current_user.role == UserRole.CUSTOMER:
        if ticket.created_by_id != current_user.id:
            raise ForbiddenAction("You do not have access to this ticket")
    elif current_user.role == UserRole.AGENT:
        if ticket.assigned_to_id != current_user.id:
            raise ForbiddenAction("You do not have access to this ticket")

    comment = Comment(
        content=comment_data.content, 
        ticketr_id=ticket.id,
        author_id=current_user.id
    )
    db.add(comment)
    db.flush()
    ActivityService.log(
        db=db,
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="COMMENT_ADDED"
    )
    return comment


@router.get("", response_model=list[CommentResponse])
def get_comments(ticket_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()

    if ticket is None:
        raise TicketNotFound()

    if current_user.role == UserRole.CUSTOMER:
        if ticket.created_by_id != current_user.id:
            raise ForbiddenAction("You do not have access to this ticket")
    elif current_user.role == UserRole.AGENT:
        if ticket.assigned_to_id != current_user.id:
            raise ForbiddenAction("You do not have access to this ticket")

    result = db.execute(select(Comment).where(Comment.ticketr_id == ticket_id).order_by(Comment.created_at))

    return result.scalars().all()