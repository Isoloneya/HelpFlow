from flask import Blueprint, request, jsonify

from app.decorators import role_required
from app.current_user import get_current_user
from app.schemas.user_schema import CreateAgentSchema, UserRoleUpdateSchema
from app.services import user_service
from app.models import UserRole

bp = Blueprint("users", __name__, url_prefix="/api/users")

create_agent_schema = CreateAgentSchema()
role_update_schema = UserRoleUpdateSchema()


@bp.route("", methods=["POST"])
@role_required(UserRole.ADMIN)
def create_agent():
    data = create_agent_schema.load(request.get_json(force=True))
    user, temp_password = user_service.create_agent(data["full_name"], data["email"])
    body = user.to_dict()
    body["temporary_password"] = temp_password
    return jsonify(body), 201


@bp.route("", methods=["GET"])
@role_required(UserRole.ADMIN, UserRole.AGENT)
def list_staff():
    users = user_service.list_staff()
    return jsonify([u.to_dict() for u in users]), 200


@bp.route("/<int:user_id>", methods=["PATCH"])
@role_required(UserRole.ADMIN)
def update_user(user_id):
    data = role_update_schema.load(request.get_json(force=True))
    user = user_service.update_user(user_id, data)
    return jsonify(user.to_dict()), 200


@bp.route("/<int:user_id>", methods=["DELETE"])
@role_required(UserRole.ADMIN)
def delete_user(user_id):
    current_user = get_current_user()
    if current_user.id == user_id:
        return jsonify({"error": {"code": "BAD_REQUEST", "message": "Неможливо видалити власний обліковий запис"}}), 400
    user_service.delete_user(user_id)
    return "", 204
