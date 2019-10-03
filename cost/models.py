from abc import abstractmethod, ABC
from typing import Dict

import requests


class CostCalculator(ABC):
    """Abstract class to implement cost calculators for different scenarios."""

    def __init__(self, job_data: Dict):
        self.job_data = job_data

    @abstractmethod
    def calculate(self) -> float:
        """Calculate final cost in USD."""
        pass


class EthereumCostCalculator(CostCalculator):
    DEFAULT_GAS_LIMIT_FOR_SINGLE_TX = 25000
    GAS_STATION_URL = 'https://ethgasstation.info/json/ethgasAPI.json'
    TO_WEI_FACTOR = 100000000
    WEI_TO_ETH_FACTOR = 1 / 1000000000000000000

    def __init__(self, cryptocompare_api_key: str, *args, **kwargs):
        self.CRYPTOCOMPARE_URL = f'https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD&api_key={cryptocompare_api_key}'
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_remote_json(url: str) -> Dict:
        """Retrieve a remote json."""
        return requests.get(url).json()

    def _get_eth_gas_station_data(self) -> Dict:
        """Retrieve json from Ethgasstation"""
        return self._get_remote_json(self.GAS_STATION_URL)

    def _get_single_tx_wei_cost(self) -> float:
        """Calculate the wei cost of a single anchoring TX on Ethereum."""
        gas_price = float(self._get_eth_gas_station_data()['average'])
        wei_gas_price = gas_price * self.TO_WEI_FACTOR
        return wei_gas_price * self.DEFAULT_GAS_LIMIT_FOR_SINGLE_TX

    def _get_eth_usd_price(self) -> float:
        """Retrieve ETH cost in USD"""
        return float(self._get_remote_json(self.CRYPTOCOMPARE_URL)['USD'])

    def _get_fixed_costs(self) -> float:
        """Calculate fixed costs for any given job to be anchored on Ethereum blockchain"""
        return self._get_single_tx_wei_cost() * self.WEI_TO_ETH_FACTOR * self._get_eth_usd_price()

    def _get_variable_costs(self) -> int:
        """Calculate costs based on the time/energy/money this job will take to process."""
        return len(self.job_data['recipients'])  # TODO: implement properly, right now simply $1/recipient

    def calculate(self) -> float:
        return self._get_fixed_costs() + self._get_variable_costs()
