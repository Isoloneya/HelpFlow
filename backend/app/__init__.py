from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, migrate, jwt
from app.models import User, Category, Ticket, Comment
from app.error_handlers import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    register_error_handlers(app)

    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.tickets import bp as tickets_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
