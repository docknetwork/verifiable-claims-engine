from voluptuous import Schema, REMOVE_EXTRA, Optional, All, Length

RECIPIENT_NAME_KEY = 'name'
RECIPIENT_EMAIL_KEY = 'identity'
RECIPIENT_PUBLIC_KEY_KEY = 'pubkey'
RECIPIENT_ADDITIONAL_FIELDS_KEY = 'additional_fields'

ISSUER_SCHEMA = Schema(
    {
        "name": str,
        "main_url": str,
        "id": str,
        "email": str,
        "logo_file": str,
        "revocation_list": str,
        "intro_url": str,
        "signature_lines": list,
        "signature_file": str,
    },
    required=True,
    extra=REMOVE_EXTRA,
)
TEMPLATE_SCHEMA = Schema(
    {
        "id": str,
        "title": str,
        "description": str,
        "criteria_narrative": str,
        "image": str,
        "additional_global_fields": list,
        "additional_per_recipient_fields": list,
        "display_html": str,
        Optional("expires_at"): str,
    },
    required=True,
    extra=REMOVE_EXTRA,
)
RECIPIENT_SCHEMA = Schema(
    All(
        [
            {
                RECIPIENT_NAME_KEY: str,
                RECIPIENT_EMAIL_KEY: str,
                RECIPIENT_PUBLIC_KEY_KEY: str,
                RECIPIENT_ADDITIONAL_FIELDS_KEY: dict,
            }
        ],
        Length(min=1)
    ),
    required=True,
    extra=REMOVE_EXTRA,
)
OUTPUT_SCHEMA = Schema(
    All(
        [
            {
                'type': str,
                'version': str,
            }
        ],
        Length(min=1)
    )
)
JOB_SCHEMA = Schema(
    {
        "blockchain": str,
        "output": OUTPUT_SCHEMA,
        Optional('eth_public_key'): str,
        Optional('eth_private_key'): str,
        Optional('eth_key_created_at'): str,
        Optional("gas_price"): int,
        Optional("gas_limit"): int,
    },
    required=True,
    extra=REMOVE_EXTRA,
)

DEFAULT_NO_SAFE_MODE = True
DEFAULT_ADDITIONAL_GLOBAL_FIELDS = '{"fields": [{"path": "$.displayHtml","value": ""}, {"path": "$.@context","value":' \
                                   ' ["https://w3id.org/openbadges/v2", "https://w3id.org/blockcerts/v2",' \
                                   ' {"displayHtml": { "@id": "schema:description" }}]}]}'
DEFAULT_ADDITIONAL_PER_RECIPIENT_FIELDS = '{"fields": [{"path": "$.displayHtml","value": "*|FOO|*","csv_column": ' \
                                          '"displayHtml"}]}'
PLACEHOLDER_RECIPIENT_NAME = "%RECIPIENT_NAME%"
PLACEHOLDER_RECIPIENT_EMAIL = "%RECIPIENT_EMAIL%"
HTML_PLACEHOLDERS = [PLACEHOLDER_RECIPIENT_NAME, PLACEHOLDER_RECIPIENT_EMAIL]
DEFAULT_DISPLAY_HTML = f'<h1>CERTIFICATE</h1><div>Awarded to:<br><b>{PLACEHOLDER_RECIPIENT_NAME}</b></div><div>With email:<br><b>{PLACEHOLDER_RECIPIENT_EMAIL}</b></div>'

BAKED_IMAGE_SUFFIX = "_baked.png"
PNG_EXTENSION = ".png"

DEFAULT_ENCODING = 'utf-8'
TEMP_PATH = "/app/temp"
ETH_PRIVATE_KEY_PATH = f"{TEMP_PATH}/keyring"
ETH_PRIVATE_KEY_FILE_NAME = "eth_private_key"
