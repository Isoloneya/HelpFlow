from marshmallow import Schema, fields, validate


class CategoryCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    sla_hours = fields.Integer(required=True, validate=validate.Range(min=1))


class CategoryUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=1, max=100))
    sla_hours = fields.Integer(validate=validate.Range(min=1))
