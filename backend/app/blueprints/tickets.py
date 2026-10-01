from flask import Blueprint, current_app, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required

from app.current_user import get_current_user
from app.decorators import role_required
from app.schemas.ticket_schema import TicketCreateSchema, TicketListSchema
from app.schemas.ticket_update_schema import TicketUpdateSchema
from app.services import ticket_service
from app.models import UserRole
from app.errors import ForbiddenError, NotFoundError

bp = Blueprint("tickets", __name__, url_prefix="/api/tickets")

ticket_create_schema = TicketCreateSchema()
ticket_update_schema = TicketUpdateSchema()
ticket_list_schema = TicketListSchema()


@bp.route("", methods=["POST"])
@jwt_required()
def create_ticket():
    user = get_current_user()

    if user.role != UserRole.CLIENT:
        raise ForbiddenError("Лише клієнт може створювати звернення")

    payload = request.get_json(force=True) if request.is_json else request.form.to_dict()
    data = ticket_create_schema.load(payload)
    ticket = ticket_service.create_ticket(user, data, request.files.getlist("files"))
    return jsonify(ticket.to_dict()), 201


@bp.route("", methods=["GET"])
@jwt_required()
def list_tickets():
    user = get_current_user()
    filters = ticket_list_schema.load(request.args)
    tickets = ticket_service.list_tickets(user, filters)
    return jsonify([t.to_dict() for t in tickets]), 200


@bp.route("/<int:ticket_id>", methods=["GET"])
@jwt_required()
def get_ticket(ticket_id):
    user = get_current_user()
    ticket = ticket_service.get_ticket(user, ticket_id)
    return jsonify(ticket.to_dict()), 200


@bp.route("/<int:ticket_id>", methods=["PATCH"])
@jwt_required()
def update_ticket(ticket_id):
    user = get_current_user()
    data = ticket_update_schema.load(request.get_json(force=True), partial=True)
    ticket = ticket_service.update_ticket(user, ticket_id, data)
    return jsonify(ticket.to_dict()), 200


@bp.route("/escalate", methods=["POST"])
@role_required(UserRole.ADMIN)
def escalate():
    overdue_count, approaching_count = ticket_service.escalate_overdue_tickets()
    return jsonify(
        {"escalated_to_urgent": overdue_count, "bumped_to_high": approaching_count}
    ), 200


@bp.route("/<int:ticket_id>/attachments/<int:attachment_id>", methods=["GET"])
@jwt_required()
def download_attachment(ticket_id, attachment_id):
    user = get_current_user()
    ticket = ticket_service.get_ticket(user, ticket_id)
    attachment = next((item for item in ticket.attachments if item.id == attachment_id), None)
    if attachment is None:
        raise NotFoundError("Вкладення не знайдено")
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        attachment.storage_name,
        download_name=attachment.filename,
    )
