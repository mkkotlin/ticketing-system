from datetime import datetime
from math import ceil
from app.enums import TicketPriority, TicketStatus, UserRole
from app.schemas import TicketAssign, TicketListResponse, TicketUpdate
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db, get_transaction
from app.models import Category, Ticket, User
from app.schemas import TicketResponse, TicketCreate
from app.dependencies import get_current_user, require_role
from app.services.ticket_service import TicketService
from app.services.activitiy_service import ActivityService

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
    # dependencies=[Depends(get_current_user)]
)

@router.get("", response_model=TicketListResponse)
def get_tickets(search: str | None = None,
                status:TicketStatus | None = None, 
                priority: TicketPriority | None = None, 
                category_id: int | None = None,
                sort_by: str = Query("created_at", pattern="^(created_at|updated_at|priority|status)$"),
                sort_order: str = Query("desc", pattern="^(asc|desc)$"), 
                page:int = Query(1, ge=1),
                limit: int = Query(10, ge=1, le=100),
                current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    statement = select(Ticket)
    if current_user.role == UserRole.CUSTOMER:
        statement = statement.where(Ticket.created_by_id == current_user.id)
    elif current_user.role == UserRole.AGENT:
        statement = statement.where(Ticket.assigned_to_id == current_user.id)
    elif current_user.role == UserRole.ADMIN:
        pass

    # ------------ADMIN------------------
    # ````````search````````
    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(Ticket.title.ilike(search_pattern) | Ticket.description.ilike(search_pattern))

    # ````````````FILTERS````````````
    if status is not None:
        statement = statement.where(Ticket.status == status)
    if priority is not None:
        statement = statement.where(Ticket.priority == priority)

    if category_id is not None:
        statement = statement.where(Ticket.category_id == category_id)


    # ````````````````COUNT ``````````````````````````
    count_statement = (select(func.count()).select_from(statement.subquery()))
    total = db.execute(count_statement).scalar_one()

    # ````````````````SORTING``````````````````````
    sort_column = getattr(Ticket, sort_by)
    if sort_order == "asc":
        statement = statement.order_by(sort_column.asc())
    else:
        statement = statement.order_by(sort_column.desc())

    if sort_by != "created_at":
        statement = statement.order_by(Ticket.created_at.desc())

    # `````````````````````PAGINATION```````````````
    offset = (page - 1) * limit
    statement = statement.offset(offset).limit(limit)

    
    # /----------------------------------
    result = db.execute(statement)
    tickets = result.scalars().all()
    pages = ceil(total / limit) if total else 0

    return {
        "items": tickets,
        "total": total,
        "page" : page,
        "limit": limit,
        "pages": pages
    }


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


@router.post("/", response_model=TicketResponse, status_code=201)
def create_ticket(ticket_data: TicketCreate, db: Session = Depends(get_transaction), current_user: User = Depends(get_current_user)):

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
    db.flush()
    ActivityService.log(db=db, ticket_id=new_ticket.id, user_id=current_user.id, action="CREATED")
    return new_ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, ticket_data: TicketUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_transaction)):
    ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    TicketService.update_ticket(db = db, ticket=ticket, current_user=current_user, data=ticket_data)
    return ticket

@router.post("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(ticket_id: int, data: TicketAssign, current_user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_transaction)):
    ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    TicketService.assign_ticket(db=db, ticket=ticket, agent_id=data.agent_id, current_user=current_user)
    return ticket


@router.post("/{ticket_id}/unassign", response_model=TicketResponse)
def unassign_ticket(ticket_id: int, current_user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_transaction)):
    ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    TicketService.unassign_ticket(ticket)
    return ticket