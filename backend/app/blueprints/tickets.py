from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.current_user import get_current_user
from app.schemas.ticket_schema import TicketCreateSchema
from app.schemas.ticket_update_schema import TicketUpdateSchema
from app.services import ticket_service
from app.models import UserRole
from app.errors import ForbiddenError

bp = Blueprint("tickets", __name__, url_prefix="/api/tickets")

ticket_create_schema = TicketCreateSchema()
ticket_update_schema = TicketUpdateSchema()


@bp.route("", methods=["POST"])
@jwt_required()
def create_ticket():
    user = get_current_user()

    if user.role != UserRole.CLIENT:
        raise ForbiddenError("Лише клієнт може створювати звернення")

    data = ticket_create_schema.load(request.get_json(force=True))
    ticket = ticket_service.create_ticket(user, data)
    return jsonify(ticket.to_dict()), 201


@bp.route("", methods=["GET"])
@jwt_required()
def list_tickets():
    user = get_current_user()
    tickets = ticket_service.list_tickets(user)
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
