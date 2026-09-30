from datetime import timedelta

from app.models import User, UserRole, Category, Ticket, TicketStatus, TicketPriority
from app.services import ticket_service
from app.utils import utcnow


def _make_ticket(db, sla_deadline, priority=TicketPriority.MEDIUM, status=TicketStatus.NEW, sla_breached=False):
    client = User.query.filter_by(email="escclient@example.com").first()
    if client is None:
        client = User(email="escclient@example.com", role=UserRole.CLIENT, password_hash="x")
        db.session.add(client)

    agent = User.query.filter_by(email="escagent@example.com").first()
    if agent is None:
        agent = User(email="escagent@example.com", role=UserRole.AGENT, password_hash="x")
        db.session.add(agent)

    category = Category.query.filter_by(name="Ескалація").first()
    if category is None:
        category = Category(name="Ескалація", sla_hours=24)
        db.session.add(category)

    db.session.commit()

    ticket = Ticket(
        title="Тікет",
        description="Опис",
        category_id=category.id,
        client_id=client.id,
        assignee_id=agent.id,
        status=status,
        priority=priority,
        sla_deadline=sla_deadline,
        sla_breached=sla_breached,
    )
    db.session.add(ticket)
    db.session.commit()
    return ticket


def test_overdue_ticket_gets_flagged_and_urgent(db):
    ticket = _make_ticket(db, utcnow() - timedelta(minutes=5), priority=TicketPriority.MEDIUM)

    overdue_count, approaching_count = ticket_service.escalate_overdue_tickets()

    db.session.refresh(ticket)
    assert overdue_count == 1
    assert ticket.sla_breached is True
    assert ticket.priority == TicketPriority.URGENT


def test_ticket_approaching_deadline_bumped_to_high(db):
    ticket = _make_ticket(db, utcnow() + timedelta(hours=1), priority=TicketPriority.LOW)

    overdue_count, approaching_count = ticket_service.escalate_overdue_tickets()

    db.session.refresh(ticket)
    assert approaching_count == 1
    assert ticket.priority == TicketPriority.HIGH
    assert ticket.sla_breached is False


def test_ticket_far_from_deadline_untouched(db):
    ticket = _make_ticket(db, utcnow() + timedelta(hours=10), priority=TicketPriority.LOW)

    overdue_count, approaching_count = ticket_service.escalate_overdue_tickets()

    db.session.refresh(ticket)
    assert overdue_count == 0
    assert approaching_count == 0
    assert ticket.priority == TicketPriority.LOW


def test_already_breached_ticket_not_recounted(db):
    _make_ticket(
        db,
        utcnow() - timedelta(hours=1),
        priority=TicketPriority.URGENT,
        sla_breached=True,
    )

    overdue_count, _ = ticket_service.escalate_overdue_tickets()

    assert overdue_count == 0


def test_closed_ticket_ignored_even_if_overdue(db):
    ticket = _make_ticket(
        db,
        utcnow() - timedelta(hours=1),
        priority=TicketPriority.MEDIUM,
        status=TicketStatus.CLOSED,
    )

    overdue_count, approaching_count = ticket_service.escalate_overdue_tickets()

    db.session.refresh(ticket)
    assert overdue_count == 0
    assert approaching_count == 0
    assert ticket.sla_breached is False


def test_urgent_priority_not_downgraded_when_approaching(db):
    ticket = _make_ticket(db, utcnow() + timedelta(hours=1), priority=TicketPriority.URGENT)

    _, approaching_count = ticket_service.escalate_overdue_tickets()

    db.session.refresh(ticket)
    assert approaching_count == 0
    assert ticket.priority == TicketPriority.URGENT
