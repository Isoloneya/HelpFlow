from marshmallow import Schema, fields, validate

from app.models import UserRole


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    role = fields.String(load_default=UserRole.CLIENT, validate=validate.OneOf(UserRole.ALL))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class ProfileUpdateSchema(Schema):
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=120))


class CreateAgentSchema(Schema):
    full_name = fields.String(load_default=None, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True)


class UserRoleUpdateSchema(Schema):
    role = fields.String(validate=validate.OneOf(UserRole.STAFF))
    is_active = fields.Boolean()
    category_ids = fields.List(fields.Integer(), validate=validate.Length(max=100))
