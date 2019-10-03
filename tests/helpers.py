import base64
import json
from functools import partial
from typing import Dict
from flask import Response
from werkzeug.test import Client

from blockcerts.const import DEFAULT_ENCODING


class JsonFlaskClient:
    """
    A tool for making tests easier, built as a wrapper around FlaskClient.

    It adds common JSON-related operations to calls and performs some of the well-known
    calls to the application views.
    """

    def __init__(self, client: Client):
        self.client = client

        # register `self.<verb>` methods for common HTTP verbs
        for verb in ['get', 'post', 'put', 'delete']:
            setattr(self, verb, partial(self._make_call, verb))

    def _make_call(
            self,
            verb: str,
            url: str,
            data: Dict = None,
            email: str = "",
            password: str = "",
            content_type='application/json',
    ) -> Response:
        action_fn = getattr(self.client, verb)
        data = data or dict()
        json_data = json.dumps(data)
        headers = self._make_headers(email, password) if email else {}
        return action_fn(
            url,
            data=json_data,
            headers=headers,
            content_type=content_type,
        )

    @staticmethod
    def _make_headers(email="", password="") -> Dict:
        """Add optional auth headers."""
        return {
            'Authorization': 'Basic ' + base64.b64encode(
                bytes(email + ":" + password, DEFAULT_ENCODING)
            ).decode(DEFAULT_ENCODING)
        }


# Dummy classes for requests.Response objects:

class Response200:
    def __init__(self):
        self.status_code = 200
        self.text = 'OK'


class Response201:
    def __init__(self):
        self.status_code = 201
        self.text = 'Created'


class Response300:
    def __init__(self):
        self.status_code = 300
        self.text = 'Multiple Choices'


class Response400:
    def __init__(self):
        self.status_code = 400
        self.text = 'Bad Request'


class Response500:
    def __init__(self):
        self.status_code = 500
        self.text = 'Internal Server Error'
