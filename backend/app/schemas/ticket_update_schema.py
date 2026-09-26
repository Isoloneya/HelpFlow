from marshmallow import Schema, fields, validate

from app.models import TicketStatus, TicketPriority


class TicketUpdateSchema(Schema):
    status = fields.String(
        validate=validate.OneOf([s.value for s in TicketStatus])
    )
    priority = fields.String(
        validate=validate.OneOf([p.value for p in TicketPriority])
    )
    assignee_id = fields.Integer()
