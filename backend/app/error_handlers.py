from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from app.errors import ApiError
from app.extensions import jwt


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return (
            jsonify({"error": {"code": err.code, "message": err.message}}),
            err.status_code,
        )

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return (
            jsonify(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Помилка валідації вхідних даних",
                        "details": err.messages,
                    }
                }
            ),
            422,
        )

    @app.errorhandler(404)
    def handle_not_found(err):
        return (
            jsonify({"error": {"code": "NOT_FOUND", "message": "Ресурс не знайдено"}}),
            404,
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        return (
            jsonify({"error": {"code": err.name.upper().replace(" ", "_"), "message": err.description}}),
            err.code,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        return (
            jsonify({"error": {"code": "INTERNAL_ERROR", "message": "Внутрішня помилка сервера"}}),
            500,
        )

    @jwt.unauthorized_loader
    def handle_missing_jwt(message):
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Потрібна автентифікація"}}), 401

    @jwt.invalid_token_loader
    def handle_invalid_jwt(message):
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Недійсний токен доступу"}}), 401

    @jwt.expired_token_loader
    def handle_expired_jwt(header, payload):
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Термін дії токена минув"}}), 401
