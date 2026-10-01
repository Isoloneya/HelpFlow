from datetime import timedelta
import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

from sqlalchemy import func, or_

from app.extensions import db
from app.models import Category, Ticket, TicketStatus, TicketPriority, User, UserRole, Attachment
from app.errors import NotFoundError, ForbiddenError, ApiError
from app.utils import utcnow

ESCALATION_THRESHOLD = timedelta(hours=2)
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024


def _least_loaded_agent(category):
    open_statuses = (TicketStatus.NEW, TicketStatus.IN_PROGRESS)

    agents = User.query.filter_by(role=UserRole.AGENT, is_active=True).all()
    if any(agent.categories for agent in agents):
        agents = [agent for agent in agents if category in agent.categories]
    if not agents:
        raise ApiError(
            "Немає агента, закріпленого за цією категорією", code="NO_AGENTS_AVAILABLE"
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


def _prepare_files(files):
    prepared_files = []
    for file in files or []:
        if not file or not file.filename:
            continue
        filename = secure_filename(file.filename)
        if not filename:
            raise ApiError("Некоректна назва файлу", code="VALIDATION_ERROR", status_code=422)
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > MAX_ATTACHMENT_SIZE:
            raise ApiError("Розмір кожного файлу не може перевищувати 10 МБ", code="VALIDATION_ERROR", status_code=422)
        prepared_files.append((file, filename))
    return prepared_files


def create_ticket(client, data, files=None):
    category = db.session.get(Category, data["category_id"])
    if category is None or category.is_archived:
        raise NotFoundError("Категорію не знайдено")

    prepared_files = _prepare_files(files)
    parent_ticket_id = data.get("parent_ticket_id")
    if parent_ticket_id is not None:
        parent_ticket = db.session.get(Ticket, parent_ticket_id)
        if parent_ticket is None or parent_ticket.client_id != client.id:
            raise NotFoundError("Початкове звернення не знайдено")

    assignee = _least_loaded_agent(category)

    ticket = Ticket(
        title=data["title"],
        description=data["description"],
        category_id=category.id,
        client_id=client.id,
        assignee_id=assignee.id,
        parent_ticket_id=data.get("parent_ticket_id"),
        status=TicketStatus.NEW,
        priority=TicketPriority(data.get("priority", TicketPriority.MEDIUM.value)),
        sla_deadline=_calculate_sla_deadline(category),
    )
    db.session.add(ticket)
    db.session.commit()
    ticket.operators.append(assignee)
    for file, filename in prepared_files:
        storage_name = f"{uuid.uuid4().hex}_{filename}"
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], storage_name)
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(path)
        attachment = Attachment(ticket_id=ticket.id, uploader_id=client.id, filename=filename, storage_name=storage_name, content_type=file.mimetype or "application/octet-stream", size=os.path.getsize(path))
        db.session.add(attachment)
    db.session.commit()
    return ticket


def _ensure_visible(user, ticket):
    if user.role == UserRole.CLIENT and ticket.client_id != user.id:
        raise ForbiddenError("У вас немає доступу до цього звернення")
    if user.role == UserRole.AGENT and user not in ticket.operators and ticket.assignee_id != user.id:
        raise ForbiddenError("Звернення призначено іншому агенту")


def get_ticket(user, ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        raise NotFoundError("Звернення не знайдено")
    _ensure_visible(user, ticket)
    return ticket


def list_tickets(user, filters=None):
    escalate_overdue_tickets()
    query = Ticket.query
    filters = filters or {}

    if user.role == UserRole.CLIENT:
        query = query.filter(Ticket.client_id == user.id)
    elif user.role == UserRole.AGENT:
        query = query.filter(or_(Ticket.assignee_id == user.id, Ticket.operators.any(User.id == user.id)))

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
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        raise NotFoundError("Звернення не знайдено")

    if user.role == UserRole.CLIENT:
        if ticket.client_id != user.id:
            raise ForbiddenError("У вас немає доступу до цього звернення")
        if data != {"status": TicketStatus.CLOSED.value}:
            raise ForbiddenError("Клієнт може лише закрити власне звернення")

    if user.role == UserRole.AGENT and user not in ticket.operators and ticket.assignee_id != user.id:
        raise ForbiddenError("Звернення призначено іншому агенту")

    if "status" in data:
        ticket.status = TicketStatus(data["status"])
    if "priority" in data:
        ticket.priority = TicketPriority(data["priority"])
    if "category_id" in data:
        category = db.session.get(Category, data["category_id"])
        if category is None or category.is_archived:
            raise NotFoundError("Категорію не знайдено")
        ticket.category_id = category.id
        ticket.category = category
        ticket.sla_deadline = _calculate_sla_deadline(category)
        ticket.sla_breached = False

    if "assignee_id" in data:
        new_assignee = db.session.get(User, data["assignee_id"])
        if new_assignee is None or new_assignee.role != UserRole.AGENT or not new_assignee.is_active:
            raise NotFoundError("Агента не знайдено")
        ticket.assignee_id = new_assignee.id
        if new_assignee not in ticket.operators:
            ticket.operators.append(new_assignee)

    if "participant_ids" in data:
        operators = User.query.filter(
            User.id.in_(data["participant_ids"]),
            User.role == UserRole.AGENT,
            User.is_active.is_(True),
        ).all()
        if len(operators) != len(set(data["participant_ids"])):
            raise NotFoundError("Одного або кількох операторів не знайдено")
        if ticket.assignee not in operators:
            operators.append(ticket.assignee)
        ticket.operators = operators

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
