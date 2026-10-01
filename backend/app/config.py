import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, "helpflow.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
load_dotenv(os.path.join(BASE_DIR, ".env"))


def get_database_url():
    url = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Config:
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY", "dev-secret-key-change-me-in-production-please"
    )
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173")
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    ALLOW_DEMO_ROLE_REGISTRATION = os.environ.get("ALLOW_DEMO_ROLE_REGISTRATION", "false").lower() == "true"
