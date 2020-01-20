import copy
import json

import pytest
from attrdict import AttrDict
from flask import url_for

from verifiable_claims.const import RECIPIENT_NAME_KEY, RECIPIENT_EMAIL_KEY
from verifiable_claims.misc import issue_certificate_batch, format_recipients


def test_issuing(app, issuer, template, three_recipients, job):
    issued_certs = issue_certificate_batch(issuer, template, three_recipients, job)
    assert isinstance(issued_certs, list)
    assert len(issued_certs) == 3
    with open('certs.json', 'w') as thisfile:
        thisfile.write(json.dumps(issued_certs[0]))

def test_issuing_then_wrapping(app, issuer, template, three_recipients, job):
    issued_certs = issue_certificate_batch(issuer, template, three_recipients, job)
    assert isinstance(issued_certs, list)
    assert len(issued_certs) == 3
    with open('certs.json', 'w') as thisfile:
        thisfile.write(json.dumps(issued_certs[0]))

    def wrap_with_vcdm(blockcert) -> dict:
        from datetime import datetime
        CURRENT_DATETIME = datetime.utcnow().isoformat()


        VCDM_TEMPLATE = AttrDict({
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://w3id.org/openbadges/v2",
                "https://gist.githubusercontent.com/faustow/3d6f830602f6d5d5fec02d2adcb0225c/raw/fdabbd02e85a83b72a4b771c43bd58ce0552e94f/blockcerts_v2_minus_proof_plus_chain.jsonld"
            ],
            "id": "",
            "type": [
                "VerifiableCredential",
                "Assertion"
            ],
            "issuer": "",
            "issuanceDate": "",
            "claim": {},
            "credentialSubject": "",
            "proof": {
                "type": "",
                "created": "",
                "jws": "",
                "proofPurpose": "",
                "verificationMethod": ""
            }
        })
        unsigned_vcdm = copy.deepcopy(VCDM_TEMPLATE)
        unsigned_vcdm.id = blockcert.id
        unsigned_vcdm.issuer = blockcert.badge.issuer.id
        unsigned_vcdm.issuanceDate = CURRENT_DATETIME
        unsigned_vcdm.claim = blockcert
        unsigned_vcdm.credentialSubject = blockcert.recipient



#
#
# def test_issuing_custom_keypair(app, issuer, template, three_recipients, job_custom_keypair_1):
#     issued_certs = issue_certificate_batch(issuer, template, three_recipients, job_custom_keypair_1)
#     assert isinstance(issued_certs, list)
#     assert len(issued_certs) == 3
#
#
# def test_issuing_empty_recipients(app, issuer, template, job_custom_keypair_1):
#     issued_certs = issue_certificate_batch(issuer, template, [], job_custom_keypair_1)
#     assert isinstance(issued_certs, list)
#     assert len(issued_certs) == 3
#
#
# @pytest.mark.parametrize("missing_key",
#                          ["name", "main_url", "id", "email", "logo_file", "revocation_list", "intro_url",
#                           "signature_lines", "signature_file"])
# def test_issuing_endpoint_issuer_missing_field(app, issuer, template, three_recipients, job, json_client, missing_key):
#     issuer.pop(missing_key)
#     assert missing_key not in issuer.keys()
#     response = json_client.post(
#         url_for('issue_certs', _external=True),
#         data=dict(
#             issuer=issuer,
#             template=template,
#             recipients=three_recipients,
#             job=job
#         )
#     )
#     assert response.status_code == 400
#     assert response.json['details'] == f"required key not provided @ data['issuer']['{missing_key}']"
#
#
# @pytest.mark.parametrize("missing_key",
#                          ["id", "title", "description", "criteria_narrative", "image", "additional_global_fields",
#                           "additional_per_recipient_fields", "display_html"])
# def test_issuing_endpoint_template_missing_field(app, issuer, template, three_recipients, job, json_client,
#                                                  missing_key):
#     template.pop(missing_key)
#     assert missing_key not in template.keys()
#     response = json_client.post(
#         url_for('issue_certs', _external=True),
#         data=dict(
#             issuer=issuer,
#             template=template,
#             recipients=three_recipients,
#             job=job
#         )
#     )
#     assert response.status_code == 400
#     assert response.json['details'] == f"required key not provided @ data['template']['{missing_key}']"
#
#
# def test_issuing_endpoint_job_missing_field(app, issuer, template, three_recipients, job, json_client):
#     job.pop('blockchain')
#     assert 'blockchain' not in job.keys()
#     response = json_client.post(
#         url_for('issue_certs', _external=True),
#         data=dict(
#             issuer=issuer,
#             template=template,
#             recipients=three_recipients,
#             job=job
#         )
#     )
#     assert response.status_code == 400
#     assert response.json['details'] == f"required key not provided @ data['job']['blockchain']"
#
#
# @pytest.mark.parametrize("missing_key", ["name", "identity", "pubkey", "additional_fields"])
# def test_issuing_endpoint_recipient_missing_field(app, issuer, template, three_recipients, job, json_client,
#                                                   missing_key):
#     three_recipients[0].pop(missing_key)
#     response = json_client.post(
#         url_for('issue_certs', _external=True),
#         data=dict(
#             issuer=issuer,
#             template=template,
#             recipients=three_recipients,
#             job=job
#         )
#     )
#     assert response.status_code == 400
#     assert response.json['details'] == f"required key not provided @ data['recipients'][0]['{missing_key}']"
#
#
# def test_issuing_endpoint_with_expiration(app, issuer, template, three_recipients, job, json_client):
#     template.expires_at = "2028-02-07T23:52:16.636+00:00"
#     response = json_client.post(
#         url_for('issue_certs', _external=True),
#         data=dict(
#             issuer=issuer,
#             template=template,
#             recipients=three_recipients,
#             job=job
#         )
#     )
#     assert isinstance(response.json, list)
#     assert len(response.json) == 3
#     assert response.json[0]['expires']
#     assert response.json[1]['expires']
#     assert response.json[2]['expires']
#
#
# def test_recipient_specific_html_creation(app, issuer, template, three_recipients, json_client):
#     template.expires_at = "2028-02-07T23:52:16.636+00:00"
#     template.display_html = '"%RECIPIENT_NAME%" - "%RECIPIENT_EMAIL%"'
#     for recipient in three_recipients:
#         assert not recipient['additional_fields']['displayHtml']
#     recipients = format_recipients(three_recipients, template, issuer)
#     for recipient in recipients:
#         assert recipient['additional_fields']['displayHtml'] == f'"{recipient.get(RECIPIENT_NAME_KEY)}" - ' \
#             f'"{recipient.get(RECIPIENT_EMAIL_KEY)}"'
#
#
# def test_issuing_endpoint_custom_keys(app, issuer, template, three_recipients, json_client, job, job_custom_keypair_1,
#                                       job_custom_keypair_2):
#     response = json_client.post(
#         url_for('issue_certs', _external=True),
#         data=dict(
#             issuer=issuer,
#             template=template,
#             recipients=three_recipients,
#             job=job
#         )
#     )
#     assert isinstance(response.json, list)
#     assert len(response.json) == 3
#
#     response_1 = json_client.post(
#         url_for('issue_certs', _external=True),
#         data=dict(
#             issuer=issuer,
#             template=template,
#             recipients=three_recipients,
#             job=job_custom_keypair_1
#         )
#     )
#     assert isinstance(response_1.json, list)
#     assert len(response_1.json) == 3
#
#     response_2 = json_client.post(
#         url_for('issue_certs', _external=True),
#         data=dict(
#             issuer=issuer,
#             template=template,
#             recipients=three_recipients,
#             job=job_custom_keypair_2
#         )
#     )
#     assert isinstance(response_2.json, list)
#     assert len(response_2.json) == 3
#
#     assert response.json[0]['verification']['publicKey'] != response_1.json[0]['verification']['publicKey'] != \
#            response_2.json[0]['verification']['publicKey']
