from datetime import timedelta

from sqlalchemy import func

from app.extensions import db
from app.models import Category, Ticket, TicketStatus, TicketPriority, User, UserRole
from app.errors import NotFoundError, ForbiddenError, ApiError
from app.utils import utcnow

ESCALATION_THRESHOLD = timedelta(hours=2)


def _least_loaded_agent():
    open_statuses = (TicketStatus.NEW, TicketStatus.IN_PROGRESS)

    agents = User.query.filter(User.role.in_(UserRole.STAFF)).all()
    if not agents:
        raise ApiError(
            "Немає доступних агентів для призначення", code="NO_AGENTS_AVAILABLE"
        )

    load_counts = dict(
        db.session.query(Ticket.assignee_id, func.count(Ticket.id))
        .filter(Ticket.status.in_(open_statuses))
        .group_by(Ticket.assignee_id)
        .all()
    )

    return min(agents, key=lambda agent: load_counts.get(agent.id, 0))


def _calculate_sla_deadline(category):
    return utcnow() + timedelta(hours=category.sla_hours)


def create_ticket(client, data):
    category = db.session.get(Category, data["category_id"])
    if category is None or category.is_archived:
        raise NotFoundError("Категорію не знайдено")

    assignee = _least_loaded_agent()

    ticket = Ticket(
        title=data["title"],
        description=data["description"],
        category_id=category.id,
        client_id=client.id,
        assignee_id=assignee.id,
        status=TicketStatus.NEW,
        priority=TicketPriority.MEDIUM,
        sla_deadline=_calculate_sla_deadline(category),
    )
    db.session.add(ticket)
    db.session.commit()
    return ticket


def _ensure_visible(user, ticket):
    if user.role == UserRole.CLIENT and ticket.client_id != user.id:
        raise ForbiddenError("У вас немає доступу до цього звернення")
    if user.role == UserRole.AGENT and ticket.assignee_id != user.id:
        raise ForbiddenError("Звернення призначено іншому агенту")


def get_ticket(user, ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        raise NotFoundError("Звернення не знайдено")
    _ensure_visible(user, ticket)
    return ticket


def list_tickets(user, filters=None):
    query = Ticket.query
    filters = filters or {}

    if user.role == UserRole.CLIENT:
        query = query.filter(Ticket.client_id == user.id)
    elif user.role == UserRole.AGENT:
        query = query.filter(Ticket.assignee_id == user.id)

    if "status" in filters:
        query = query.filter(Ticket.status == TicketStatus(filters["status"]))
    if "priority" in filters:
        query = query.filter(Ticket.priority == TicketPriority(filters["priority"]))
    if "assignee_id" in filters:
        query = query.filter(Ticket.assignee_id == filters["assignee_id"])
    if "category_id" in filters:
        query = query.filter(Ticket.category_id == filters["category_id"])

    return query.order_by(Ticket.created_at.desc()).all()


def update_ticket(user, ticket_id, data):
    if user.role == UserRole.CLIENT:
        raise ForbiddenError("У вас немає прав на зміну звернення")

    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        raise NotFoundError("Звернення не знайдено")

    if user.role == UserRole.AGENT and ticket.assignee_id != user.id:
        raise ForbiddenError("Звернення призначено іншому агенту")

    if "status" in data:
        ticket.status = TicketStatus(data["status"])
    if "priority" in data:
        ticket.priority = TicketPriority(data["priority"])
    if "assignee_id" in data:
        if user.role != UserRole.ADMIN:
            raise ForbiddenError("Лише адміністратор може перепризначати звернення")
        new_assignee = db.session.get(User, data["assignee_id"])
        if new_assignee is None or new_assignee.role not in UserRole.STAFF:
            raise NotFoundError("Агента не знайдено")
        ticket.assignee_id = new_assignee.id

    db.session.commit()
    return ticket


def escalate_overdue_tickets():
    now = utcnow()
    open_statuses = (TicketStatus.NEW, TicketStatus.IN_PROGRESS)

    overdue = Ticket.query.filter(
        Ticket.status.in_(open_statuses),
        Ticket.sla_deadline <= now,
        Ticket.sla_breached.is_(False),
    ).all()

    for ticket in overdue:
        ticket.sla_breached = True
        ticket.priority = TicketPriority.URGENT

    approaching = Ticket.query.filter(
        Ticket.status.in_(open_statuses),
        Ticket.sla_deadline > now,
        Ticket.sla_deadline <= now + ESCALATION_THRESHOLD,
        Ticket.priority.in_((TicketPriority.LOW, TicketPriority.MEDIUM)),
    ).all()

    for ticket in approaching:
        ticket.priority = TicketPriority.HIGH

    db.session.commit()
    return len(overdue), len(approaching)
