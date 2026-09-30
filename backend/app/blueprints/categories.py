from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.decorators import role_required
from app.schemas.category_schema import CategoryCreateSchema, CategoryUpdateSchema
from app.services import category_service
from app.models import UserRole

bp = Blueprint("categories", __name__, url_prefix="/api/categories")

category_create_schema = CategoryCreateSchema()
category_update_schema = CategoryUpdateSchema()


@bp.route("", methods=["POST"])
@role_required(UserRole.ADMIN)
def create_category():
    data = category_create_schema.load(request.get_json(force=True))
    category = category_service.create_category(data)
    return jsonify(category.to_dict()), 201


@bp.route("", methods=["GET"])
@jwt_required()
def list_categories():
    categories = category_service.list_categories()
    return jsonify([c.to_dict() for c in categories]), 200


@bp.route("/<int:category_id>", methods=["PATCH"])
@role_required(UserRole.ADMIN)
def update_category(category_id):
    data = category_update_schema.load(request.get_json(force=True), partial=True)
    category = category_service.update_category(category_id, data)
    return jsonify(category.to_dict()), 200


@bp.route("/<int:category_id>", methods=["DELETE"])
@role_required(UserRole.ADMIN)
def delete_category(category_id):
    category = category_service.delete_category(category_id)
    if category is None:
        return "", 204
    return jsonify(category.to_dict()), 200
