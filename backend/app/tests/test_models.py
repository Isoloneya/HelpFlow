from datetime import datetime, timedelta, timezone

from app.models import (
    User,
    UserRole,
    Category,
    Ticket,
    TicketStatus,
    TicketPriority,
    Comment,
)


def test_create_user(db):
    user = User(email="client@example.com", role=UserRole.CLIENT)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    saved = User.query.filter_by(email="client@example.com").first()
    assert saved is not None
    assert saved.role == UserRole.CLIENT
    assert saved.check_password("password123")
    assert not saved.check_password("wrong")


def test_user_email_must_be_unique(db):
    db.session.add(User(email="dup@example.com", role=UserRole.CLIENT, password_hash="x"))
    db.session.commit()

    db.session.add(User(email="dup@example.com", role=UserRole.CLIENT, password_hash="x"))
    try:
        db.session.commit()
        assert False, "мало бути порушення унікальності email"
    except Exception:
        db.session.rollback()


def test_create_category(db):
    category = Category(name="Технічна підтримка", sla_hours=24)
    db.session.add(category)
    db.session.commit()

    saved = Category.query.filter_by(name="Технічна підтримка").first()
    assert saved is not None
    assert saved.sla_hours == 24
    assert saved.is_archived is False


def test_create_ticket_with_relations(db):
    client = User(email="client2@example.com", role=UserRole.CLIENT, password_hash="x")
    agent = User(email="agent2@example.com", role=UserRole.AGENT, password_hash="x")
    category = Category(name="Білінг", sla_hours=8)
    db.session.add_all([client, agent, category])
    db.session.commit()

    ticket = Ticket(
        title="Проблема з оплатою",
        description="Клієнт не може оплатити рахунок",
        category_id=category.id,
        client_id=client.id,
        assignee_id=agent.id,
        status=TicketStatus.NEW,
        priority=TicketPriority.HIGH,
        sla_deadline=datetime.now(timezone.utc) + timedelta(hours=8),
    )
    db.session.add(ticket)
    db.session.commit()

    saved = Ticket.query.first()
    assert saved.status == TicketStatus.NEW
    assert saved.priority == TicketPriority.HIGH
    assert saved.category.name == "Білінг"
    assert saved.client.email == "client2@example.com"
    assert saved.assignee.email == "agent2@example.com"


def test_create_comment_internal_flag(db):
    client = User(email="client3@example.com", role=UserRole.CLIENT, password_hash="x")
    agent = User(email="agent3@example.com", role=UserRole.AGENT, password_hash="x")
    category = Category(name="Доступ", sla_hours=4)
    db.session.add_all([client, agent, category])
    db.session.commit()

    ticket = Ticket(
        title="Не можу увійти",
        description="Забув пароль",
        category_id=category.id,
        client_id=client.id,
        assignee_id=agent.id,
        sla_deadline=datetime.now(timezone.utc) + timedelta(hours=4),
    )
    db.session.add(ticket)
    db.session.commit()

    public_comment = Comment(
        ticket_id=ticket.id, author_id=client.id, body="Будь ласка, допоможіть"
    )
    internal_note = Comment(
        ticket_id=ticket.id,
        author_id=agent.id,
        body="Клієнт уже звертався минулого тижня",
        is_internal=True,
    )
    db.session.add_all([public_comment, internal_note])
    db.session.commit()

    saved_ticket = Ticket.query.first()
    assert len(saved_ticket.comments) == 2
    internal = [c for c in saved_ticket.comments if c.is_internal]
    assert len(internal) == 1
    assert internal[0].author.email == "agent3@example.com"
