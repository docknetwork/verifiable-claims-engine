import copy
from typing import List

from attrdict import AttrDict

from flaskapp.config import get_config
from flaskapp.errors import ValidationError
from verifiable_claims.const import PLACEHOLDER_RECIPIENT_NAME, PLACEHOLDER_RECIPIENT_EMAIL, \
    ETH_PRIVATE_KEY_PATH, ETH_PRIVATE_KEY_FILE_NAME, \
    HTML_PLACEHOLDERS, RECIPIENT_NAME_KEY, RECIPIENT_EMAIL_KEY
from verifiable_claims.issuer.simple import SimplifiedCertificateBatchIssuer
from verifiable_claims.tools.cert_tools.create_v2_certificate_template import create_certificate_template
from verifiable_claims.tools.cert_tools.instantiate_v2_certificate_batch import create_unsigned_certificates_from_roster


def write_private_key_file(private_key: str) -> None:
    """Write the given ETH Private Key to the default key file."""
    with open(f"{ETH_PRIVATE_KEY_PATH}/{ETH_PRIVATE_KEY_FILE_NAME}", mode='w') as private_key_file:
        private_key_file.write(private_key)


def get_display_html_for_recipient(recipient: AttrDict, template: AttrDict) -> str:
    """Take the template's displayHtml and replace placeholders in it."""
    result = copy.deepcopy(template.display_html)
    replacements = [
        (PLACEHOLDER_RECIPIENT_NAME, recipient.get(RECIPIENT_NAME_KEY)),
        (PLACEHOLDER_RECIPIENT_EMAIL, recipient.get(RECIPIENT_EMAIL_KEY))
    ]
    for key, value in replacements:
        if value:
            result = result.replace(key, value)
    return result


def issue_certificate_batch(issuer_data: AttrDict, template_data: AttrDict, recipients_data: List,
                            job_data: AttrDict) -> List:
    """Issue a batch of certificates and return them as a list."""
    job_config = get_job_config(job_data)
    ensure_valid_issuer_data(issuer_data)
    ensure_valid_template_data(template_data)
    tools_config = get_tools_config(issuer_data, template_data, job_config)
    issuer_config = get_issuer_config(job_data, job_config)
    recipients = format_recipients(recipients_data, template_data, issuer_data)
    template = create_certificate_template(tools_config)
    unsigned_certs = create_unsigned_certificates_from_roster(
        template,
        recipients,
        False,
        tools_config.additional_per_recipient_fields,
        tools_config.hash_emails
    )
    simple_certificate_batch_issuer = SimplifiedCertificateBatchIssuer(issuer_config, unsigned_certs)
    tx_id, signed_certs = simple_certificate_batch_issuer.issue()
    return list(signed_certs.values())


def get_job_config(job_data: AttrDict) -> AttrDict:
    """Returns the overall config modified by inputs in the job section"""
    config = get_config()
    config = AttrDict(dict((k.lower(), v) for k, v in config.items()))
    if job_data.get('eth_public_key') and job_data.get('eth_private_key') and job_data.get('eth_key_created_at'):
        config.eth_public_key = job_data.eth_public_key
        config.eth_private_key = job_data.eth_private_key
        config.eth_key_created_at = job_data.eth_key_created_at
    return AttrDict(config)


def get_tools_config(issuer: AttrDict, template: AttrDict, job_config: AttrDict) -> AttrDict:
    if template.get('expires_at'):
        template.additional_global_fields = template.additional_global_fields + (
            {"path": "$.expires", "value": template.get('expires_at')},
        )
    return AttrDict(
        no_files=True,
        issuer_logo_file=issuer.logo_file,
        cert_image_file=template.image,
        issuer_url=issuer.main_url,
        issuer_intro_url=issuer.intro_url,
        issuer_email=issuer.email,
        issuer_name=issuer.name,
        issuer_id=issuer.id,
        certificate_description=template.description,
        certificate_title=template.title,
        criteria_narrative=template.criteria_narrative,
        hash_emails=False,
        revocation_list_uri=issuer.revocation_list,
        issuer_public_key=job_config.get('eth_public_key'),
        badge_id=str(template.id),
        issuer_signature_lines=issuer.signature_lines,
        issuer_signature_file=issuer.signature_file,
        additional_global_fields=template.additional_global_fields,
        additional_per_recipient_fields=template.additional_per_recipient_fields,
        display_html=template.display_html,
        public_key_created_at=job_config.get('eth_key_created_at'),
    )


def get_issuer_config(job: AttrDict, job_config: AttrDict) -> AttrDict:
    eth_public_key = job_config.get('eth_public_key').split(':')[1] if ":" in job_config.get(
        'eth_public_key') else job_config.get('eth_public_key')
    return AttrDict(
        issuing_address=eth_public_key,
        chain=job.blockchain,
        usb_name=ETH_PRIVATE_KEY_PATH,
        key_file=ETH_PRIVATE_KEY_FILE_NAME,
        eth_private_key=job_config.get('eth_private_key'),
        unsigned_certificates_dir="",
        blockchain_certificates_dir="",
        work_dir="",
        safe_mode=False,
        gas_price=job.gas_price,
        gas_limit=job.gas_limit,
        api_token="",
    )


def ensure_valid_issuer_data(issuer: AttrDict) -> None:
    """Validate the issuer object has all needed properties."""
    if not issuer.logo_file:
        raise ValidationError('issuer needs a logo file before it is able to issue')


def ensure_valid_template_data(template: AttrDict) -> None:
    """Validate the template object has all needed properties."""
    if not template.image:
        raise ValidationError('template needs an image file before it can be used to issue')


def format_recipients(recipients_data: List, template_data: AttrDict, issuer_data: AttrDict) -> List:
    """Replace placeholders with the right data the given template uses them in display_html."""
    if any(word in template_data.display_html for word in HTML_PLACEHOLDERS):
        for recipient in recipients_data:
            recipient['additional_fields']['displayHtml'] = get_display_html_for_recipient(recipient, template_data)
    return recipients_data
