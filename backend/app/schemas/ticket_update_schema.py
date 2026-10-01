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
    category_id = fields.Integer()
    participant_ids = fields.List(fields.Integer(), validate=validate.Length(min=1, max=20))
