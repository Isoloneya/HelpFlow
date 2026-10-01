import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Attachment, Comment, Ticket, TicketStatus, UserRole
from app.errors import ApiError, NotFoundError, ForbiddenError

MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024


def _get_ticket_for_comment(user, ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        raise NotFoundError("Звернення не знайдено")

    if user.role == UserRole.CLIENT and ticket.client_id != user.id:
        raise ForbiddenError("У вас немає доступу до цього звернення")
    if user.role == UserRole.AGENT and user not in ticket.operators and ticket.assignee_id != user.id:
        raise ForbiddenError("Звернення призначено іншому агенту")

    return ticket


def create_comment(user, ticket_id, data, files=None):
    ticket = _get_ticket_for_comment(user, ticket_id)
    if ticket.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
        raise ApiError("Листування для вирішеного або закритого звернення недоступне", code="TICKET_CLOSED", status_code=409)

    is_internal = data.get("is_internal", False)
    if is_internal and user.role not in UserRole.STAFF:
        raise ForbiddenError(
            "Внутрішні нотатки доступні лише агентам і адміністраторам"
        )

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

    if not data["body"].strip() and not prepared_files:
        raise ApiError("Напишіть повідомлення або додайте файл", code="VALIDATION_ERROR", status_code=422)

    comment = Comment(
        ticket_id=ticket.id,
        author_id=user.id,
        body=data["body"].strip(),
        is_internal=is_internal,
    )
    db.session.add(comment)
    db.session.commit()
    for file, filename in prepared_files:
        storage_name = f"{uuid.uuid4().hex}_{filename}"
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)
        path = os.path.join(upload_folder, storage_name)
        file.save(path)
        db.session.add(Attachment(
            ticket_id=ticket.id,
            comment_id=comment.id,
            uploader_id=user.id,
            filename=filename,
            storage_name=storage_name,
            content_type=file.mimetype or "application/octet-stream",
            size=os.path.getsize(path),
        ))
    db.session.commit()
    return comment


def list_comments(user, ticket_id):
    ticket = _get_ticket_for_comment(user, ticket_id)

    comments = ticket.comments
    if user.role == UserRole.CLIENT:
        comments = [c for c in comments if not c.is_internal]

    return comments
