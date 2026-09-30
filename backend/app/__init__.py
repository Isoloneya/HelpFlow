from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, migrate, jwt, cors
from app.models import User, Category, Ticket, Comment
from app.error_handlers import register_error_handlers
from app.cli import register_cli


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"].split(","))

    register_error_handlers(app)
    register_cli(app)

    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.tickets import bp as tickets_bp
    from app.blueprints.comments import bp as comments_bp
    from app.blueprints.categories import bp as categories_bp
    from app.blueprints.users import bp as users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(users_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
