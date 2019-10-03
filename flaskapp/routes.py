from attrdict import AttrDict
from flask import jsonify, request
from voluptuous import Schema, REMOVE_EXTRA

from blockcerts.const import ISSUER_SCHEMA, TEMPLATE_SCHEMA, RECIPIENT_SCHEMA
from blockcerts.misc import issue_certificate_batch


def setup_routes(app):
    @app.route('/ping')
    def ping_route():
        return jsonify({'reply': 'pong'})

    @app.route('/issue', methods=['POST'])
    def issue_certs():
        issuing_job_schema = Schema(
            {
                'issuer': ISSUER_SCHEMA,
                'template': TEMPLATE_SCHEMA,
                'recipients': RECIPIENT_SCHEMA,
            },
            required=True,
            extra=REMOVE_EXTRA,
        )
        payload = issuing_job_schema(request.get_json())
        batch = issue_certificate_batch(
            AttrDict(payload['issuer']),
            AttrDict(payload['template']),
            [AttrDict(rec) for rec in payload['recipients']],
        )
        return jsonify(batch)
