from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.current_user import get_current_user
from app.schemas.comment_schema import CommentCreateSchema
from app.services import comment_service

bp = Blueprint(
    "comments", __name__, url_prefix="/api/tickets/<int:ticket_id>/comments"
)

comment_create_schema = CommentCreateSchema()


@bp.route("", methods=["POST"])
@jwt_required()
def create_comment(ticket_id):
    user = get_current_user()
    data = comment_create_schema.load(request.get_json(force=True))
    comment = comment_service.create_comment(user, ticket_id, data)
    return jsonify(comment.to_dict()), 201


@bp.route("", methods=["GET"])
@jwt_required()
def list_comments(ticket_id):
    user = get_current_user()
    comments = comment_service.list_comments(user, ticket_id)
    return jsonify([c.to_dict() for c in comments]), 200
