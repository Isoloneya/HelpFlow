from marshmallow import Schema, fields, validate

from app.models import UserRole


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class CreateAgentSchema(Schema):
    email = fields.Email(required=True)


class UserRoleUpdateSchema(Schema):
    role = fields.String(required=True, validate=validate.OneOf(UserRole.ALL))
