from attrdict import AttrDict
from flask import jsonify, request
from voluptuous import Schema, REMOVE_EXTRA

from blockcerts.const import ISSUER_SCHEMA, TEMPLATE_SCHEMA, RECIPIENT_SCHEMA, JOB_SCHEMA
from blockcerts.misc import issue_certificate_batch, get_tx_receipt, verify_cert
from flaskapp.config import get_config


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
                'job': JOB_SCHEMA,
            },
            required=True,
            extra=REMOVE_EXTRA,
        )
        payload = issuing_job_schema(request.get_json())
        tx_id, signed_certs = issue_certificate_batch(
            AttrDict(payload['issuer']),
            AttrDict(payload['template']),
            [AttrDict(rec) for rec in payload['recipients']],
            AttrDict(payload['job']),
        )
        return jsonify(dict(
            tx_id=tx_id,
            signed_certificates=list(signed_certs.values())
        ))

    @app.route('/config', methods=['GET'])
    def public_config():
        config = get_config()
        return jsonify(
            dict(
                ETH_PUBLIC_KEY=config.get('ETH_PUBLIC_KEY'),
                ETH_KEY_CREATED_AT=config.get('ETH_KEY_CREATED_AT'),
            )
        )

    @app.route('/tx/<chain>/<tx_id>', methods=['GET'])
    def tx_receipt(chain, tx_id):
        receipt = get_tx_receipt(chain, tx_id)
        if receipt:
            return jsonify(dict(receipt)), 200
        return f"Tx '{tx_id}' not found in chain '{chain}'.", 404

    @app.route('/verify', methods=['POST'])
    def verify():
        payload = request.get_json()
        results = verify_cert(payload)
        return jsonify(dict(
            verified=results[0],
            steps=results[1]
        ))
