from typing import Dict

from flask import Flask

from blockcerts.misc import write_private_key_file
from flaskapp.config import parse_config, set_config
from flaskapp.errors import register_errors
from flaskapp.routes import setup_routes


def create_app(config_data: Dict) -> Flask:
    app = Flask(__name__)

    app.config.update(parse_config(config_data))
    set_config(app.config)
    register_errors(app)
    setup_routes(app)
    write_private_key_file(app.config.get('ETH_PRIVATE_KEY'))
    return app
