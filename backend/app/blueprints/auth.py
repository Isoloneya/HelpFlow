from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.schemas.user_schema import RegisterSchema, LoginSchema
from app.services import auth_service
from app.current_user import get_current_user

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

register_schema = RegisterSchema()
login_schema = LoginSchema()


@bp.route("/register", methods=["POST"])
def register():
    data = register_schema.load(request.get_json(force=True))
    user = auth_service.register_client(data["email"], data["password"])
    return jsonify(user.to_dict()), 201


@bp.route("/login", methods=["POST"])
def login():
    data = login_schema.load(request.get_json(force=True))
    user, token = auth_service.authenticate(data["email"], data["password"])
    return jsonify({"access_token": token, "user": user.to_dict()}), 200


@bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = get_current_user()
    return jsonify(user.to_dict()), 200
