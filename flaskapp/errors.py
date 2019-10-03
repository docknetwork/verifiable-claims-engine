import re
from typing import Any

import voluptuous
from flask import jsonify, Response
from werkzeug.exceptions import HTTPException


def register_errors(app):
    @app.errorhandler(404)
    def handle_not_found_error(error: Exception) -> Response:
        return ResourceNotFound(details=str(error)).jsonify()

    @app.errorhandler(500)
    def handle_validation_error(error: Exception) -> Response:
        return ServerError(details=str(error)).jsonify()

    @app.errorhandler(AppError)
    def handle_invalid_usage(error: Exception) -> Response:
        return error.jsonify()

    @app.errorhandler(voluptuous.MultipleInvalid)
    @app.errorhandler(voluptuous.Invalid)
    def handle_validation_error(error: Exception) -> Response:
        return ValidationError(details=str(error)).jsonify()


class AppError(HTTPException):
    code = 400

    def __init__(self, key: str = None, details: Any = None, code: int = None):
        super(AppError, self).__init__()
        self.key = key
        if code:
            self.code = code
        self.details = details

    @classmethod
    def slugify_exception_name(cls):
        return re.sub(r'(?<=[a-z])(?=[A-Z])', '-', cls.__name__).lower()

    def get_response(self, environ=None):
        return self.jsonify()

    def jsonify(self):
        error_obj = {
            'error': self.slugify_exception_name(),
            'key': self.key,
            'details': self.details,
        }

        res = jsonify(error_obj)
        res.status_code = self.code

        return res


class ValidationError(AppError):
    pass


class ObjectExists(AppError):
    code = 409


class Unauthorized(AppError):
    code = 401


class Forbidden(AppError):
    code = 403


class ResourceNotFound(AppError):
    code = 404


class ServerError(AppError):
    code = 500
