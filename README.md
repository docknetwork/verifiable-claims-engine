# Verifiable Claims Engine
![](https://github.com/docknetwork/verifiable-claims-engine/workflows/pytest/badge.svg)

Python reference implementation of a verifiable claims issuing engine.

## Motivation

Credentials are a part of our daily lives: from driver's licenses used to assert that we are capable of operating a vehicle, to university degrees used to assert our level of education. This repo provides a Rest API to issue digital verifiable claims or credentials in a way that is cryptographically secure, privacy respecting, and machine-verifiable.

Additionally, this application contains modules for bidding and cost calculation, which are essential capabilities of a full *issuing node* in the [Dock Network](http://dock.io).

Although much of the issuing-related code was initially forked off the original `cert-tools` and `cert-issuer` repos, it has been significantly modified to achieve two core improvements:
1. In-memory issuing: the original code relies heavily on filesystem usage for intermediate files, which causes race conditions and concurrency issues.
1. Trustless anchoring: the anchoring process no longer needs to go through a third party API, you can now use your own Ethereum node for increased security.

Additionally, the code has been composed into a dockerized, easy to use and well-tested application which exposes an endpoint that summarizes all the different steps needed across different repos in order to perform standards-compliant verifiable claims issuing.

## Module-specific Readmes

- [Claims issuing](blockcerts/README.md)
- [Cost](cost/README.md)
- [Bidding](bidding/README.md)

## Development info

This is a [flask](https://flask.palletsprojects.com/en/1.1.x/)-based REST API that has been [Docker](https://www.docker.com/)ized for easier development work and deployments.

Anchoring to Ethereum (the only fully-tested blockchain option for anchoring) is done using [web3py](https://web3py.readthedocs.io/en/stable/).


### Build image
Before you can try this code out you will want to *build* a docker image with it, you can achieve that by running:
```bash
docker build -t verifiable-claims-engine --build-arg DEV=1 .
```
This process will take a few minutes depending on various factors like your internet connection's download speed.

### Run tests
Once the image has been built you may want to run the unittests to make sure everything is working properly. To do that from outside the container you can run the following command:
```bash
docker run -it --rm --name verifiable-claims-engine  --mount type=bind,source=$(pwd),target=/app verifiable-claims-engine pytest tests
```

### Bash inside container
Having a built image you may also want to run a container with that image and then access bash inside it. That's easily achieved by running:
```bash
docker run -it --rm --name verifiable-claims-engine  --mount type=bind,source=$(pwd),target=/app verifiable-claims-engine bash
```
Once inside the running container you can execute unittests with `pytest tests`, edit the environment or spawn a python cli for example; all in a linux box setup and configured the way a full issuing node would be.


#### Instantiate app in python cli
During your development work, you may need to try things out inside a running application. To do that first bash into the container and then execute `python`. Once inside the python CLI you can run:
```python
import os
from flaskapp.app import create_app
app = create_app(config_data=os.environ)
```
which gives you a running application (in `app`) so you can access all the methods and data structures that the full running application has access to.


## Run the Verifiable Claims Engine
If you want to try issuing verifiable claims directly, you first need to run the container and the `verifiable-claims-engine` application exposing a port from the container to the outside world. 

In the following example command we're doing just that, and exposing the container's port 80 as port 8080
```bash
docker run -it --rm --name verifiable-claims-engine --mount type=bind,source=$(pwd),target=/app -p 8080:80 verifiable-claims-engine
```
To verify the application is running try doing a GET request to the address http://127.0.0.1:8080/ping .

## Issue your own verifiable claims!
Once you have your `verifiable-claims-engine` application running in a local container over at http://127.0.0.1:8080 issuing can be achieved by doing a POST call to http://127.0.0.1:8080/issue. 

As you may have guessed, the information contained in the payload you submit to this endpoint will be used as the basis to manufacture the final verifiable claims, so let's examine its structure.

### Issuing payload structure

The `/issue` endpoint expects a JSON payload (so remember setting the `Content-Type: application/json` header). The payload should be a JSON object (python dict) with the following structure (all keys are **required**):
```
{
	"issuer":{},
	"template":{},
	"recipients":[]
}
```

#### Issuer
The `issuer` key contains a JSON object with information about the issuing organization or authority claiming something about each of the given recipients or *subjects*. Here's a list of the accepted keys:
- name
- main_url
- id
- email
- logo_file
- revocation_list
- intro_url
- signature_lines
- signature_file

For more info please visit the [specs](https://www.imsglobal.org/sites/default/files/Badges/OBv2p0Final/index.html).

#### Template
The `template` key contains a JSON object with info about the assertion or *claim* being made by the *issuer* about each recipient or *subject*. It may contain the following keys:
- id
- title
- description
- criteria_narrative
- image
- additional_global_fields
- additional_per_recipient_fields
- display_html
- blockchain
- gas_price
- gas_limit

For more info please visit the [specs](https://www.imsglobal.org/sites/default/files/Badges/OBv2p0Final/index.html).


#### Recipients
The `recipients` key contains an array of JSON objects, each with info about specific recipient or *subject* of the *claim* made by the *issuer*. Each recipient object may contain the following keys:
- name
- identity
- pubkey
- additional_fields

For more info please visit the [specs](https://www.imsglobal.org/sites/default/files/Badges/OBv2p0Final/index.html).

### Issuing payload sample
The following is a sample curl call to the `/issue` endpoint that should result in fully standards compliant verifiable claims (please note that strings representing base64-encoded images or html code have been truncated to improve readability):
```bash
curl -X POST \
  http://127.0.0.1:8080/issue \
  -H 'Content-Type: application/json' \
  -d '{
  "issuer":{
        "name": "Verifiable",
        "main_url": "https://verifiable.com",
        "id": "https://gist.githubusercontent.com/faustow/98db76b26b4d297d0eb98d499e733f77/raw/30610aa20c28297e0c5c82490676bf9b354877c6/newissuer.json",
        "email": "hello@verifiable.com",
        "logo_file": "data:image/png;base64,iVBORw0...",
        "revocation_list": "https://gist.githubusercontent.com/faustow/07a66855d713409067ff28e10778e2dd/raw/e08bb6d6f1350367d3f6d4f805ab3b1466b584d7/revocation-list-testnet.json",
        "intro_url": "https://verifiable.com",
        "signature_lines": [
            {
                "job_title": "University Issuer",
                "signature_image": "data:image/png;base64,iVBORw0...",
                "name": "Your signature"
            }
        ],
        "signature_file": "data:image/png;base64,iVBORw0..."
    },
  "template":{
        "id": "123Y-UI12-3YUI",
        "title": "Nuclear Powerplant Operator",
        "description": "Operators know how to run the plant.",
        "criteria_narrative": "Candidates are tested on...",
        "image": "data:image/png;base64,iVBORw....",
        "additional_global_fields": [
            {"path": "$.displayHtml", "value": ""},
            {
                "path": "$.@context",
                "value": [
                    "https://w3id.org/openbadges/v2",
                    "https://w3id.org/blockcerts/v2",
                    {"displayHtml": {"@id": "schema:description"}}
                ]
            }
        ],
        "additional_per_recipient_fields": [{"path": "$.displayHtml", "value": "*|FOO|*", "csv_column": "displayHtml"}],
        "display_html": "<div class=...",
        "blockchain": "ethereum_ropsten",
        "gas_price": 20000000000,
        "gas_limit": 25000
    },
  "recipients":[
        {
            "name": "Fausto",
            "identity": "phaws@mail.com",
            "pubkey": "ecdsa-koblitz-pubkey:123ghj123ghj123",
            "additional_fields": {"displayHtml":""}
        },
        {
            "name": "John",
            "identity": "john@mail.com",
            "pubkey": "ecdsa-koblitz-pubkey:123ghj123ghj123",
            "additional_fields": {"displayHtml":""}
        },
        {
            "name": "Ben",
            "identity": "ben@mail.com",
            "pubkey": "ecdsa-koblitz-pubkey:123ghj123ghj123",
            "additional_fields": {"displayHtml":""}
        }
    ]
}'
```
Provided that you changed the truncated strings by valid base64-encoded images or HTML where required, this call should produce a JSON response with three standards-compliant verifiable claims. 

Please note that whether these credentials pass a validation process depends heavily on the input data (for example eventual `200` for any given url). This documentation won't dive further into the verification process, for more info about that please refer to the [specs](https://www.imsglobal.org/sites/default/files/Badges/OBv2p0Final/index.html).


***

## Bugs and feature requests

For bugs and feature requests please contact [Fausto Woelflin](https://github.com/faustow) at the [Dock Foundation](http://dock.io).
