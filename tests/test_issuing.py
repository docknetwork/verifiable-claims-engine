import pytest
from flask import url_for

from blockcerts.const import RECIPIENT_NAME_KEY, RECIPIENT_EMAIL_KEY
from blockcerts.misc import issue_certificate_batch, format_recipients


def test_issuing(app, issuer, template, three_recipients):
    issued_certs = issue_certificate_batch(issuer, template, three_recipients)
    assert isinstance(issued_certs, list)
    assert len(issued_certs) == 3


def test_issuing_endpoint(app, issuer, template, three_recipients, json_client):
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
        )
    )
    assert isinstance(response.json, list)
    assert len(response.json) == 3
    assert 'expires' not in response.json[0].keys()
    assert 'expires' not in response.json[1].keys()
    assert 'expires' not in response.json[2].keys()


def test_issuing_endpoint_empty_recipients(app, issuer, template, json_client):
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=[],
        )
    )
    assert response.status_code == 400
    assert response.json['details'] == "length of value must be at least 1 for dictionary value @ data['recipients']"


@pytest.mark.parametrize("missing_key",
                         ["name", "main_url", "id", "email", "logo_file", "revocation_list", "intro_url",
                          "signature_lines", "signature_file"])
def test_issuing_endpoint_issuer_missing_field(app, issuer, template, three_recipients, json_client, missing_key):
    issuer.pop(missing_key)
    assert missing_key not in issuer.keys()
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
        )
    )
    assert response.status_code == 400
    assert response.json['details'] == f"required key not provided @ data['issuer']['{missing_key}']"


@pytest.mark.parametrize("missing_key",
                         ["id", "title", "description", "criteria_narrative", "image", "additional_global_fields",
                          "additional_per_recipient_fields", "display_html", "blockchain"])
def test_issuing_endpoint_template_missing_field(app, issuer, template, three_recipients, json_client, missing_key):
    template.pop(missing_key)
    assert missing_key not in template.keys()
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
        )
    )
    assert response.status_code == 400
    assert response.json['details'] == f"required key not provided @ data['template']['{missing_key}']"


@pytest.mark.parametrize("missing_key", ["name", "identity", "pubkey", "additional_fields"])
def test_issuing_endpoint_recipient_missing_field(app, issuer, template, three_recipients, json_client, missing_key):
    three_recipients[0].pop(missing_key)
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
        )
    )
    assert response.status_code == 400
    assert response.json['details'] == f"required key not provided @ data['recipients'][0]['{missing_key}']"


def test_issuing_endpoint_with_expiration(app, issuer, template, three_recipients, json_client):
    template.expires_at = "2028-02-07T23:52:16.636+00:00"
    response = json_client.post(
        url_for('issue_certs', _external=True),
        data=dict(
            issuer=issuer,
            template=template,
            recipients=three_recipients,
        )
    )
    assert isinstance(response.json, list)
    assert len(response.json) == 3
    assert response.json[0]['expires']
    assert response.json[1]['expires']
    assert response.json[2]['expires']


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
