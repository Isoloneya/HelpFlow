import pytest

from app.services import ticket_service
from app.models import User, UserRole, Category, Ticket, TicketStatus
from app.errors import NotFoundError, ApiError
from app.utils import utcnow


def _make_client(db, email="client@example.com"):
    client = User(email=email, role=UserRole.CLIENT, password_hash="x")
    db.session.add(client)
    db.session.commit()
    return client


def _make_agent(db, email):
    agent = User(email=email, role=UserRole.AGENT, password_hash="x")
    db.session.add(agent)
    db.session.commit()
    return agent


def _make_category(db, sla_hours=24, name="Загальні питання"):
    category = Category(name=name, sla_hours=sla_hours)
    db.session.add(category)
    db.session.commit()
    for agent in User.query.filter_by(role=UserRole.AGENT).all():
        agent.categories.append(category)
    db.session.commit()
    return category


def test_create_ticket_sets_sla_deadline(db):
    client = _make_client(db)
    _make_agent(db, "agent1@example.com")
    category = _make_category(db, sla_hours=8)

    before = utcnow()
    ticket = ticket_service.create_ticket(
        client, {"title": "Проблема", "description": "Опис", "category_id": category.id}
    )

    hours_diff = (ticket.sla_deadline - before).total_seconds() / 3600
    assert 7.9 <= hours_diff <= 8.1
    assert ticket.status == TicketStatus.NEW


def test_create_ticket_raises_on_missing_category(db):
    client = _make_client(db)
    _make_agent(db, "agent2@example.com")

    with pytest.raises(NotFoundError):
        ticket_service.create_ticket(
            client, {"title": "T", "description": "D", "category_id": 999}
        )


def test_create_ticket_raises_when_no_agents(db):
    client = _make_client(db)
    category = _make_category(db)

    with pytest.raises(ApiError):
        ticket_service.create_ticket(
            client, {"title": "T", "description": "D", "category_id": category.id}
        )


def test_assigns_to_least_loaded_agent(db):
    client = _make_client(db)
    agent_a = _make_agent(db, "agent_a@example.com")
    agent_b = _make_agent(db, "agent_b@example.com")
    category = _make_category(db)

    first = ticket_service.create_ticket(
        client, {"title": "Перше", "description": "Опис", "category_id": category.id}
    )
    assert first.assignee_id in (agent_a.id, agent_b.id)

    second = ticket_service.create_ticket(
        client, {"title": "Друге", "description": "Опис", "category_id": category.id}
    )

    assert second.assignee_id != first.assignee_id


def test_third_ticket_still_balances_load(db):
    client = _make_client(db)
    agent_a = _make_agent(db, "agent_c@example.com")
    agent_b = _make_agent(db, "agent_d@example.com")
    category = _make_category(db)

    tickets = [
        ticket_service.create_ticket(
            client,
            {"title": f"Тікет {i}", "description": "Опис", "category_id": category.id},
        )
        for i in range(4)
    ]

    counts = {}
    for t in tickets:
        counts[t.assignee_id] = counts.get(t.assignee_id, 0) + 1

    assert counts[agent_a.id] == 2
    assert counts[agent_b.id] == 2


def test_ticket_is_assigned_to_agent_not_admin(db):
    client = _make_client(db)
    admin = User(email="admin@example.com", role=UserRole.ADMIN, password_hash="x")
    db.session.add(admin)
    db.session.commit()
    agent = _make_agent(db, "onlyagent@example.com")
    category = _make_category(db)

    ticket = ticket_service.create_ticket(
        client, {"title": "Тікет", "description": "Опис", "category_id": category.id}
    )

    assert ticket.assignee_id == agent.id
