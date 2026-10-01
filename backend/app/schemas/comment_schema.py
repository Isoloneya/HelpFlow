from marshmallow import Schema, fields, validate


class CommentCreateSchema(Schema):
    body = fields.String(load_default="", validate=validate.Length(max=2000))
    is_internal = fields.Boolean(load_default=False)
