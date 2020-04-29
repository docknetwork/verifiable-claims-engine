from typing import Dict

from flask import Config

# All config passed to `create_app()` is filtered through this list. That means that if you wish to
# introduce a new config variable, you need to add it here, otherwise it will not be available. 
# Each triple represents a config variable: (<name>, <type>, <default value>).
CONFIG_VARS = [
    ('TESTING', bool, False),
    ('DEBUG', bool, False),
    ('ETH_PUBLIC_KEY', str, None),
    ('ETH_PRIVATE_KEY', str, None),
    ('ETH_KEY_CREATED_AT', str, None),
    ('ETH_NODE_URL_ROPSTEN', str, None),
    ('ETH_NODE_URL_MAINNET', str, None),
    ('ETHERSCAN_API_TOKEN', str, None),
]

_global_config = None


def parse_config(config_data: Dict) -> Dict:
    config = {}
    for var_name, var_type, default_value in CONFIG_VARS:
        value = config_data.get(var_name, default_value)
        value = _convert(value, var_type)
        config[var_name] = value
    return config


def set_config(config: Config) -> None:
    global _global_config
    _global_config = config


def get_config() -> Config:
    return _global_config


def _convert(value, var_type):
    if type(value) is var_type or value is None:
        return value

    if var_type in [str, int, float]:
        return var_type(value)

    if var_type is bool:
        if isinstance(value, str):
            return value.lower() in ['true', 'yes', 'y', '1', 't']
        else:
            return bool(value)

    raise NotImplementedError('Unknown config var type', var_type)
