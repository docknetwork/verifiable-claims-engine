import copy
from datetime import datetime
from typing import List

from attrdict import AttrDict

from blockcerts.const import HTML_DATE_FORMAT, PLACEHOLDER_RECIPIENT_NAME, PLACEHOLDER_RECIPIENT_EMAIL, \
    PLACEHOLDER_ISSUING_DATE, PLACEHOLDER_ISSUER_LOGO, PLACEHOLDER_ISSUER_SIGNATURE_FILE, PLACEHOLDER_EXPIRATION_DATE, \
    PLACEHOLDER_CERT_TITLE, PLACEHOLDER_CERT_DESCRIPTION, ETH_PRIVATE_KEY_PATH, ETH_PRIVATE_KEY_FILE_NAME, \
    HTML_PLACEHOLDERS, RECIPIENT_NAME_KEY, RECIPIENT_EMAIL_KEY
from blockcerts.issuer.cert_issuer.simple import SimplifiedCertificateBatchIssuer
from blockcerts.tools.cert_tools.create_v2_certificate_template import create_certificate_template
from blockcerts.tools.cert_tools.instantiate_v2_certificate_batch import create_unsigned_certificates_from_roster
from flaskapp.config import get_config
from flaskapp.errors import ValidationError


def write_private_key_file(private_key: str) -> None:
    """Write the given ETH Private Key to the default key file."""
    with open(f"{ETH_PRIVATE_KEY_PATH}/{ETH_PRIVATE_KEY_FILE_NAME}", mode='w') as private_key_file:
        private_key_file.write(private_key)


# def bake_cert(issued_cert: IssuedCert) -> str:
#     """Bake the contents of an issued cert into the template's PNG file."""
# from openbadges_bakery import utils as bakery_utils

#     write_temp_image(issued_cert.template.image)
#     source_path = get_temp_filepath_for_image(issued_cert.template.image)
#     destination_path = f"{DEFAULT_TEMP_IMAGE_DIR_PATH}/{get_temp_filename_for_baked_image(issued_cert)}"
#     source = open(source_path, 'rb')
#     destination = open(destination_path, 'wb')
#
#     bakery_utils.bake(
#         source,
#         json.dumps(issued_cert.contents),
#         destination,
#     )
#
#     return get_temp_filename_for_baked_image(issued_cert)


# def unbake_cert(path_to_png_file: str) -> str:
#     """Return the string stored inside a baked cert."""
#     baked_image = open(path_to_png_file, 'rb')
#     return bakery_utils.unbake(baked_image)


def get_display_html_for_recipient(recipient: AttrDict, template: AttrDict, issuer: AttrDict) -> str:
    """Take the template's displayHtml and replace placeholders in it."""
    expiration = template.get('expires_at') or 'None'
    result = copy.deepcopy(template.display_html)
    replacements = [
        (PLACEHOLDER_RECIPIENT_NAME, recipient.get(RECIPIENT_NAME_KEY)),
        (PLACEHOLDER_RECIPIENT_EMAIL, recipient.get(RECIPIENT_EMAIL_KEY)),
        (PLACEHOLDER_ISSUING_DATE, datetime.utcnow().strftime(HTML_DATE_FORMAT)),
        (PLACEHOLDER_ISSUER_LOGO, str(issuer.logo_file)),
        (PLACEHOLDER_ISSUER_SIGNATURE_FILE, issuer.signature_file),
        (PLACEHOLDER_EXPIRATION_DATE, expiration),
        (PLACEHOLDER_CERT_TITLE, template.title),
        (PLACEHOLDER_CERT_DESCRIPTION, template.description),
    ]
    for key, value in replacements:
        if value:
            result = result.replace(key, value)
    return result


def issue_certificate_batch(issuer_data: AttrDict, template_data: AttrDict, recipients_data: List) -> List:
    """The final step where all the blockcerts magic happens."""
    ensure_valid_issuer_data(issuer_data)
    ensure_valid_template_data(template_data)
    tools_config = get_tools_config(issuer_data, template_data)
    issuer_config = get_issuer_config(template_data)
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


def get_tools_config(issuer: AttrDict, template: AttrDict) -> AttrDict:
    config = get_config()
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
        issuer_public_key=config.get('ETH_PUBLIC_KEY'),
        badge_id=str(template.id),
        issuer_signature_lines=issuer.signature_lines,
        issuer_signature_file=issuer.signature_file,
        additional_global_fields=template.additional_global_fields,
        additional_per_recipient_fields=template.additional_per_recipient_fields,
        display_html=template.display_html,
        public_key_created_at=config.get('ETH_KEY_CREATED_AT'),
    )


def get_issuer_config(template: AttrDict) -> AttrDict:
    config = get_config()
    return AttrDict(
        issuing_address=config.get('ETH_PUBLIC_KEY').split(':')[1],
        chain=template.blockchain,
        usb_name=ETH_PRIVATE_KEY_PATH,
        key_file=ETH_PRIVATE_KEY_FILE_NAME,
        unsigned_certificates_dir="",
        blockchain_certificates_dir="",
        work_dir="",
        safe_mode=False,
        gas_price=template.gas_price,
        gas_limit=template.gas_limit,
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
            recipient['additional_fields']['displayHtml'] = get_display_html_for_recipient(
                recipient, template_data, issuer_data
            )
    return recipients_data
