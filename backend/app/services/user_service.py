import secrets

from app.extensions import db
from app.models import User, UserRole, Ticket, TicketStatus, Category
from app.errors import NotFoundError, ConflictError, ApiError


def create_agent(full_name, email):
    existing = User.query.filter_by(email=email).first()
    if existing:
        raise ConflictError("Користувач із таким email вже існує")

    temp_password = secrets.token_urlsafe(9)

    user = User(full_name=full_name or email.split("@", 1)[0], email=email, role=UserRole.AGENT)
    user.set_password(temp_password)
    db.session.add(user)
    db.session.commit()
    return user, temp_password


def create_admin(email, password, full_name="Адміністратор"):
    existing = User.query.filter_by(email=email).first()
    if existing:
        raise ConflictError("Користувач із таким email вже існує")

    user = User(full_name=full_name, email=email, role=UserRole.ADMIN)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def list_staff():
    return User.query.filter(User.role.in_(UserRole.STAFF)).order_by(User.created_at).all()


def update_user(user_id, data):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("Користувача не знайдено")

    if "is_active" in data and not data["is_active"]:
        has_open_tickets = Ticket.query.filter(
            Ticket.assignee_id == user.id,
            Ticket.status.in_((TicketStatus.NEW, TicketStatus.IN_PROGRESS)),
        ).first()
        if has_open_tickets:
            raise ConflictError("Неможливо деактивувати працівника з активними зверненнями")

    if "role" in data:
        user.role = data["role"]
    if "is_active" in data:
        user.is_active = data["is_active"]

    if "category_ids" in data:
        if user.role not in UserRole.STAFF:
            raise ApiError("Категорії можна призначати лише працівникам", code="VALIDATION_ERROR", status_code=422)
        categories = Category.query.filter(
            Category.id.in_(data["category_ids"]), Category.is_archived.is_(False)
        ).all()
        if len(categories) != len(set(data["category_ids"])):
            raise NotFoundError("Одну або кілька категорій не знайдено")
        user.categories = categories
    db.session.commit()
    return user


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("Користувача не знайдено")

    has_tickets = Ticket.query.filter(
        (Ticket.client_id == user.id) | (Ticket.assignee_id == user.id)
    ).first()
    if has_tickets:
        raise ConflictError("Неможливо видалити користувача зі зверненнями")

    db.session.delete(user)
    db.session.commit()
