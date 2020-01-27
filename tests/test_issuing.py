from unittest import mock

import pytest
from flask import url_for

from blockcerts.const import RECIPIENT_NAME_KEY, RECIPIENT_EMAIL_KEY
from blockcerts.misc import issue_certificate_batch, format_recipients, get_tx_receipt


def test_issuing(app, issuer, template, three_recipients, job):
    tx_id, issued_certs = issue_certificate_batch(issuer, template, three_recipients, job)
    assert isinstance(issued_certs, dict)
    assert len(issued_certs) == 3


def test_issuing_custom_keypair(app, issuer, template, three_recipients, job_custom_keypair_1):
    tx_id, issued_certs = issue_certificate_batch(issuer, template, three_recipients, job_custom_keypair_1)
    assert isinstance(issued_certs, dict)
    assert len(issued_certs) == 3


def test_issuing_endpoint(app, issuer, template, three_recipients, job, json_client):
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
            job=job
        )
    )
    assert isinstance(response.json, dict)
    signed_certificates = response.json['signed_certificates']
    assert isinstance(signed_certificates, list)
    assert len(signed_certificates) == 3
    assert 'expires' not in signed_certificates[0].keys()
    assert 'expires' not in signed_certificates[1].keys()
    assert 'expires' not in signed_certificates[2].keys()


def test_issuing_endpoint_empty_recipients(app, issuer, template, job, json_client):
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=[],
            job=job
        )
    )
    assert response.status_code == 400
    assert response.json['details'] == "length of value must be at least 1 for dictionary value @ data['recipients']"


@pytest.mark.parametrize("missing_key",
                         ["name", "main_url", "id", "email", "logo_file", "revocation_list", "intro_url",
                          "signature_lines", "signature_file"])
def test_issuing_endpoint_issuer_missing_field(app, issuer, template, three_recipients, job, json_client, missing_key):
    issuer.pop(missing_key)
    assert missing_key not in issuer.keys()
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
            job=job
        )
    )
    assert response.status_code == 400
    assert response.json['details'] == f"required key not provided @ data['issuer']['{missing_key}']"


@pytest.mark.parametrize("missing_key",
                         ["id", "title", "description", "criteria_narrative", "image", "additional_global_fields",
                          "additional_per_recipient_fields", "display_html"])
def test_issuing_endpoint_template_missing_field(app, issuer, template, three_recipients, job, json_client,
                                                 missing_key):
    template.pop(missing_key)
    assert missing_key not in template.keys()
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
            job=job
        )
    )
    assert response.status_code == 400
    assert response.json['details'] == f"required key not provided @ data['template']['{missing_key}']"


def test_issuing_endpoint_job_missing_field(app, issuer, template, three_recipients, job, json_client):
    job.pop('blockchain')
    assert 'blockchain' not in job.keys()
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
            job=job
        )
    )
    assert response.status_code == 400
    assert response.json['details'] == f"required key not provided @ data['job']['blockchain']"


@pytest.mark.parametrize("missing_key", ["name", "identity", "pubkey", "additional_fields"])
def test_issuing_endpoint_recipient_missing_field(app, issuer, template, three_recipients, job, json_client,
                                                  missing_key):
    three_recipients[0].pop(missing_key)
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
            job=job
        )
    )
    assert response.status_code == 400
    assert response.json['details'] == f"required key not provided @ data['recipients'][0]['{missing_key}']"


def test_issuing_endpoint_with_expiration(app, issuer, template, three_recipients, job, json_client):
    template.expires_at = "2028-02-07T23:52:16.636+00:00"
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
            job=job
        )
    )

    assert isinstance(response.json, dict)
    signed_certificates = response.json['signed_certificates']
    assert isinstance(signed_certificates, list)
    assert len(signed_certificates) == 3
    assert signed_certificates[0]['expires']
    assert signed_certificates[1]['expires']
    assert signed_certificates[2]['expires']


def test_recipient_specific_html_creation(app, issuer, template, three_recipients, json_client):
    template.expires_at = "2028-02-07T23:52:16.636+00:00"
    template.display_html = '"%RECIPIENT_NAME%" - "%RECIPIENT_EMAIL%" - "%ISSUING_DATE%" "%ISSUER_LOGO%" ' \
                            '"%ISSUER_SIGNATURE_FILE%" "%EXPIRATION_DATE%"  "%CERT_TITLE%" "%CERT_DESCRIPTION%"'
    for recipient in three_recipients:
        assert not recipient['additional_fields']['displayHtml']
    recipients = format_recipients(three_recipients, template, issuer)
    for recipient in recipients:
        assert recipient['additional_fields']['displayHtml'].startswith(f'"{recipient.get(RECIPIENT_NAME_KEY)}" - '
                                                                        f'"{recipient.get(RECIPIENT_EMAIL_KEY)}" - "')
        assert recipient['additional_fields']['displayHtml'].endswith(f'"{template.expires_at}"  "{template.title}" '
                                                                      f'"{template.description}"')


def test_issuing_endpoint_custom_keys(app, issuer, template, three_recipients, json_client, job, job_custom_keypair_1,
                                      job_custom_keypair_2):
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
            job=job
        )
    )

    assert isinstance(response.json, dict)
    signed_certificates = response.json['signed_certificates']
    assert isinstance(signed_certificates, list)
    assert len(signed_certificates) == 3

    response_1 = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
            job=job_custom_keypair_1
        )
    )

    assert isinstance(response_1.json, dict)
    signed_certificates_1 = response_1.json['signed_certificates']
    assert isinstance(signed_certificates_1, list)
    assert len(signed_certificates_1) == 3

    response_2 = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
            job=job_custom_keypair_2
        )
    )

    assert isinstance(response_2.json, dict)
    signed_certificates_2 = response_2.json['signed_certificates']
    assert isinstance(signed_certificates_2, list)
    assert len(signed_certificates_2) == 3

    assert signed_certificates[0]['verification']['publicKey'] != signed_certificates_1[0]['verification'][
        'publicKey'] != signed_certificates_2[0]['verification']['publicKey']


def test_tx_receipt(app):
    tx_receipt = get_tx_receipt('ropsten', '0x36d7c25a79b3a32f0bfa59547f837f62ced399a8a700a6f00147ddd5339b2505')
    assert tx_receipt
    assert isinstance(tx_receipt, dict)


def test_tx_receipt_endpoint(app, json_client):
    response = json_client.get('/tx/ropsten/0x36d7c25a79b3a32f0bfa59547f837f62ced399a8a700a6f00147ddd5339b2505')
    assert response
    assert response.status_code == 200
    assert response.json['blockHash'] == '0x09f1b0e57f5e6a84280084d39da157cf806b28d090e78159d5e24041d8d93fe2'


@mock.patch('flaskapp.routes.get_tx_receipt', return_value=None)
def test_tx_receipt_endpoint_missing_tx(app, json_client):
    response = json_client.get('/tx/ropsten/0x36d7c25a79b3a32f0bfa59547f837f62ced399a8a700a6f00147ddd5339b2505')
    assert not response.json
    assert response.status_code == 404


def test_tx_receipt_endpoint_wrong_tx(app, json_client):
    wrong_tx_id = '123'
    response = json_client.get(f'/tx/ropsten/{wrong_tx_id}')
    assert response.json == {
        'details': None, 'error': 'validation-error',
        'key': f"Transaction with hash '{wrong_tx_id}' not found."
    }
    assert response.status_code == 400


def test_issuing_endpoint_with_per_recipient_expiration(app, issuer, template, three_recipients, job, json_client):
    three_recipients[0].additional_fields = {'expires': '2018-01-07T23:52:16.636+00:00'}
    three_recipients[1].additional_fields = {'expires': '2028-02-07T23:52:16.636+00:00'}
    three_recipients[2].additional_fields = {'expires': '2038-03-07T23:52:16.636+00:00'}
    template.additional_per_recipient_fields = (
        template.additional_per_recipient_fields[0],
        {"path": "$.expires", "value": "", "csv_column": "expires"}
    )

    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
            job=job
        )
    )

    assert isinstance(response.json, dict)
    signed_certificates = response.json['signed_certificates']
    assert isinstance(signed_certificates, list)
    assert len(signed_certificates) == 3

    assert signed_certificates[0]['expires'] == three_recipients[0].additional_fields['expires']
    assert signed_certificates[1]['expires'] == three_recipients[1].additional_fields['expires']
    assert signed_certificates[2]['expires'] == three_recipients[2].additional_fields['expires']
