from flask import jsonify
from marshmallow import ValidationError

from app.errors import ApiError


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
