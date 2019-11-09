from flask import url_for


def test_issuing_endpoint(app, json_client):
    response = json_client.get(
        url_for('public_config', _external=True),
    )
    assert 'ETH_KEY_CREATED_AT' in response.json.keys()
    assert 'ETH_PUBLIC_KEY' in response.json.keys()
