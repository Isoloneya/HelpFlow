from app.extensions import db
from app.models import Category
from app.errors import NotFoundError, ConflictError


def create_category(data):
    existing = Category.query.filter_by(name=data["name"]).first()
    if existing:
        raise ConflictError("Категорія з такою назвою вже існує")

    category = Category(name=data["name"], sla_hours=data["sla_hours"])
    db.session.add(category)
    db.session.commit()
    return category


def list_categories(include_archived=False):
    query = Category.query
    if not include_archived:
        query = query.filter_by(is_archived=False)
    return query.order_by(Category.name).all()


def update_category(category_id, data):
    category = db.session.get(Category, category_id)
    if category is None:
        raise NotFoundError("Категорію не знайдено")

    if "name" in data:
        existing = Category.query.filter(
            Category.name == data["name"], Category.id != category.id
        ).first()
        if existing:
            raise ConflictError("Категорія з такою назвою вже існує")
        category.name = data["name"]
    if "sla_hours" in data:
        category.sla_hours = data["sla_hours"]

    db.session.commit()
    return category


def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if category is None:
        raise NotFoundError("Категорію не знайдено")

    if category.has_tickets():
        category.is_archived = True
        db.session.commit()
        return category

    db.session.delete(category)
    db.session.commit()
    return None
