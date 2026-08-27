from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Ticket, TicketActivity, User
from ..schemas import TicketActivityResponse


router = APIRouter(
    prefix="/tickets/{ticket_id}/activities",
    tags=["Ticket Activities"]
)

@router.get(
    "",
    response_model=list[TicketActivityResponse]
)
def get_activities(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.execute(
        select(Ticket).where(
            Ticket.id == ticket_id
        )
    ).scalar_one_or_none()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # CUSTOMER → own ticket
    if current_user.role == "CUSTOMER":
        if ticket.created_by_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this ticket"
            )

    # AGENT → assigned ticket
    elif current_user.role == "AGENT":
        if ticket.assigned_to_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this ticket"
            )

    result = db.execute(
        select(TicketActivity)
        .where(
            TicketActivity.ticket_id == ticket_id
        )
        .order_by(
            TicketActivity.created_at.asc()
        )
    )

    return result.scalars().all()