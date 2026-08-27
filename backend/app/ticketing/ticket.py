from datetime import datetime
from app.enums import TicketPriority, TicketStatus, UserRole
from app.schemas import TicketAssign, TicketUpdate
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Ticket, User
from app.schemas import TicketResponse, TicketCreate
from app.dependencies import get_current_user, require_role
from ..services.ticket_service import TicketService

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
    # dependencies=[Depends(get_current_user)]
)

@router.get("", response_model=list[TicketResponse])
def get_tickets(status:TicketStatus | None = None, 
                priority: TicketPriority | None = None, 
                category_id: int | None = None, 
                page:int = Query(1, ge=1),
                limit: int = Query(10, ge=1, le=100)
                , current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    statement = select(Ticket)
    if current_user.role == UserRole.CUSTOMER:
        statement = statement.where(Ticket.created_by_id == current_user.id)
    elif current_user.role == UserRole.AGENT:
        statement = statement.where(Ticket.assigned_to_id == current_user.id)
    elif current_user.role == UserRole.ADMIN:
        pass

    # ------------ADMIN------------------
    if status is not None:
        statement = statement.where(Ticket.status == status)
    if priority is not None:
        statement = statement.where(Ticket.priority == priority)

    if category_id is not None:
        statement = statement.where(Ticket.category_id == category_id)

    offset = (page - 1) * limit
    statement = (statement.order_by(Ticket.created_at.desc()).offset(offset).limit(limit))

    
    # /----------------------------------
    result = db.execute(statement)
    return result.scalars().all()


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    statement = select(Ticket).where(Ticket.id == ticket_id)
    ticket = db.execute(statement).scalar_one_or_none()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role == UserRole.CUSTOMER:
        if ticket.created_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="You do not have access to this ticket")
    elif current_user.role == UserRole.AGENT:
        if ticket.assigned_to_id != current_user.id:
            raise HTTPException(status_code=403, detail="You do not have access to this ticket")
    return ticket


@router.post("/", response_model=TicketResponse)
def create_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    category = db.execute(select(Category).where(Category.id == ticket_data.category_id)).scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="category not found")
    new_ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        category_id=ticket_data.category_id,
        priority=ticket_data.priority,
        created_by_id=current_user.id
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, ticket_data: TicketUpdate, current_user: User =Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    TicketService.update_ticket(db = db, ticket=ticket, current_user=current_user, data=ticket_data)
    db.commit()
    db.refresh(ticket)
    return ticket

@router.post("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(data: TicketAssign, ticket_id: int, current_user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_db)):
    ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    TicketService.assign_ticket(db=db, ticket=ticket, agent_id=data.agent_id)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.post("/{ticket_id}/unassign", response_model=TicketResponse)
def unassign_ticket(ticket_id: int, current_user: User = Depends(require_role(UserRole.ADMIN)),db: Session = Depends(get_db)):
    ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    TicketService.unassign_ticket(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket