import logging
import os

from flaskapp.app import create_app

log = logging.getLogger(__name__)
app = create_app(config_data=os.environ)

if __name__ == '__main__':
    log.info('Serving requests')
    app.run(host='0.0.0.0', port=80)
