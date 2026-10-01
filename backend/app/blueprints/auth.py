from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import jwt_required

from app.schemas.user_schema import RegisterSchema, LoginSchema, ProfileUpdateSchema
from app.services import auth_service
from app.current_user import get_current_user

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

register_schema = RegisterSchema()
login_schema = LoginSchema()
profile_update_schema = ProfileUpdateSchema()


@bp.route("/register", methods=["POST"])
def register():
    data = register_schema.load(request.get_json(force=True))
    user = auth_service.register_user(
        data["email"],
        data["password"],
        data["role"],
        current_app.config["ALLOW_DEMO_ROLE_REGISTRATION"],
    )
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


@bp.route("/me", methods=["PATCH"])
@jwt_required()
def update_me():
    user = get_current_user()
    data = profile_update_schema.load(request.get_json(force=True))
    user.full_name = data["full_name"]
    from app.extensions import db
    db.session.commit()
    return jsonify(user.to_dict()), 200
