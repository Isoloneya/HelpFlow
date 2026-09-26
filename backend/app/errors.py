class ApiError(Exception):
    code = "BAD_REQUEST"
    status_code = 400

    def __init__(self, message, code=None, status_code=None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code


class NotFoundError(ApiError):
    code = "NOT_FOUND"
    status_code = 404


class ForbiddenError(ApiError):
    code = "FORBIDDEN"
    status_code = 403


class ConflictError(ApiError):
    code = "CONFLICT"
    status_code = 409


class UnauthorizedError(ApiError):
    code = "UNAUTHORIZED"
    status_code = 401
