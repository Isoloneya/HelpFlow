from marshmallow import Schema, fields, validate


class CommentCreateSchema(Schema):
    body = fields.String(required=True, validate=validate.Length(min=1, max=2000))
    is_internal = fields.Boolean(load_default=False)
