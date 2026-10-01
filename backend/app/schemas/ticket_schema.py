from marshmallow import Schema, fields, validate

from app.models import TicketStatus, TicketPriority


class TicketCreateSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=150))
    description = fields.String(
        required=True, validate=validate.Length(min=1, max=5000)
    )
    category_id = fields.Integer(required=True)
    parent_ticket_id = fields.Integer(load_default=None)
    priority = fields.String(
        load_default=TicketPriority.MEDIUM.value,
        validate=validate.OneOf([p.value for p in TicketPriority]),
    )


class TicketListSchema(Schema):
    status = fields.String(validate=validate.OneOf([s.value for s in TicketStatus]))
    priority = fields.String(
        validate=validate.OneOf([p.value for p in TicketPriority])
    )
    assignee_id = fields.Integer()
    category_id = fields.Integer()
