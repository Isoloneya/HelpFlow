import pytest

from app.models import User, UserRole, Category, Ticket, TicketStatus, TicketPriority
from app.services import comment_service
from app.errors import NotFoundError, ForbiddenError
from app.utils import utcnow


def _make_ticket(db, client_email="client@example.com", agent_email="agent@example.com"):
    client = User(email=client_email, role=UserRole.CLIENT, password_hash="x")
    agent = User(email=agent_email, role=UserRole.AGENT, password_hash="x")
    category = Category(name="Категорія", sla_hours=24)
    db.session.add_all([client, agent, category])
    db.session.commit()

    ticket = Ticket(
        title="Тікет",
        description="Опис",
        category_id=category.id,
        client_id=client.id,
        assignee_id=agent.id,
        status=TicketStatus.NEW,
        priority=TicketPriority.MEDIUM,
        sla_deadline=utcnow(),
    )
    db.session.add(ticket)
    db.session.commit()

    return client, agent, ticket


def test_client_can_create_public_comment(db):
    client, agent, ticket = _make_ticket(db)

    comment = comment_service.create_comment(
        client, ticket.id, {"body": "Питання від клієнта"}
    )

    assert comment.is_internal is False
    assert comment.author_id == client.id


def test_client_cannot_create_internal_comment(db):
    client, agent, ticket = _make_ticket(db)

    with pytest.raises(ForbiddenError):
        comment_service.create_comment(
            client, ticket.id, {"body": "Спроба", "is_internal": True}
        )


def test_agent_can_create_internal_comment(db):
    client, agent, ticket = _make_ticket(db)

    comment = comment_service.create_comment(
        agent, ticket.id, {"body": "Внутрішня нотатка", "is_internal": True}
    )

    assert comment.is_internal is True


def test_other_client_cannot_comment_on_foreign_ticket(db):
    client, agent, ticket = _make_ticket(db)
    other_client = User(email="other@example.com", role=UserRole.CLIENT, password_hash="x")
    db.session.add(other_client)
    db.session.commit()

    with pytest.raises(ForbiddenError):
        comment_service.create_comment(
            other_client, ticket.id, {"body": "Чужий тікет"}
        )


def test_create_comment_raises_on_missing_ticket(db):
    client = User(email="lonely@example.com", role=UserRole.CLIENT, password_hash="x")
    db.session.add(client)
    db.session.commit()

    with pytest.raises(NotFoundError):
        comment_service.create_comment(client, 999, {"body": "Немає тікета"})


def test_client_does_not_see_internal_comments(db):
    client, agent, ticket = _make_ticket(db)
    comment_service.create_comment(client, ticket.id, {"body": "Публічне"})
    comment_service.create_comment(
        agent, ticket.id, {"body": "Внутрішнє", "is_internal": True}
    )

    visible = comment_service.list_comments(client, ticket.id)

    assert len(visible) == 1
    assert visible[0].is_internal is False


def test_agent_sees_all_comments(db):
    client, agent, ticket = _make_ticket(db)
    comment_service.create_comment(client, ticket.id, {"body": "Публічне"})
    comment_service.create_comment(
        agent, ticket.id, {"body": "Внутрішнє", "is_internal": True}
    )

    visible = comment_service.list_comments(agent, ticket.id)

    assert len(visible) == 2
