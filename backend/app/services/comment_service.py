from app.extensions import db
from app.models import Comment, Ticket, UserRole
from app.errors import NotFoundError, ForbiddenError


def _get_ticket_for_comment(user, ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        raise NotFoundError("Звернення не знайдено")

    if user.role == UserRole.CLIENT and ticket.client_id != user.id:
        raise ForbiddenError("У вас немає доступу до цього звернення")

    return ticket


def create_comment(user, ticket_id, data):
    ticket = _get_ticket_for_comment(user, ticket_id)

    is_internal = data.get("is_internal", False)
    if is_internal and user.role not in UserRole.STAFF:
        raise ForbiddenError(
            "Внутрішні нотатки доступні лише агентам і адміністраторам"
        )

    comment = Comment(
        ticket_id=ticket.id,
        author_id=user.id,
        body=data["body"],
        is_internal=is_internal,
    )
    db.session.add(comment)
    db.session.commit()
    return comment


def list_comments(user, ticket_id):
    ticket = _get_ticket_for_comment(user, ticket_id)

    comments = ticket.comments
    if user.role == UserRole.CLIENT:
        comments = [c for c in comments if not c.is_internal]

    return comments
