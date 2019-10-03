from unittest import mock

from cost.models import EthereumCostCalculator


class TestEthereumCosts:
    ETH_GASSTATION_JSON = {'fast': 60.0, 'fastest': 200.0, 'safeLow': 10.0, 'average': 10.0,
                           'block_time': 13.048780487804878, 'blockNum': 8356493, 'speed': 0.8607744113116175,
                           'safeLowWait': 3.8, 'avgWait': 3.8, 'fastWait': 0.5, 'fastestWait': 0.4}
    CRYPTOCOMPARE_JSON = {'USD': 184.6}

    @mock.patch('cost.models.EthereumCostCalculator._get_remote_json', return_value=ETH_GASSTATION_JSON)
    def test_single_tx_wei_cost(self, _):
        calc = EthereumCostCalculator(cryptocompare_api_key='some_api_key', job_data={})
        single_tx_cost = calc._get_single_tx_wei_cost()
        assert single_tx_cost == 25000000000000
        assert isinstance(single_tx_cost, float)

    @mock.patch('cost.models.EthereumCostCalculator._get_remote_json', return_value=CRYPTOCOMPARE_JSON)
    def test_eth_usd_price(self, _):
        calc = EthereumCostCalculator(cryptocompare_api_key='some_api_key', job_data={})
        eth_usd_price = calc._get_eth_usd_price()
        assert eth_usd_price == 184.6
        assert isinstance(eth_usd_price, float)

    @mock.patch('cost.models.EthereumCostCalculator._get_eth_gas_station_data', return_value=ETH_GASSTATION_JSON)
    @mock.patch('cost.models.EthereumCostCalculator._get_eth_usd_price', return_value=184.6)
    def test_get_fixed_costs(self, _, __):
        calc = EthereumCostCalculator(cryptocompare_api_key='some_api_key', job_data={})
        assert calc._get_fixed_costs() == 0.004615

    @mock.patch('cost.models.EthereumCostCalculator._get_eth_gas_station_data', return_value=ETH_GASSTATION_JSON)
    @mock.patch('cost.models.EthereumCostCalculator._get_eth_usd_price', return_value=184.6)
    def test_get_variable_costs(self, _, __):
        calc = EthereumCostCalculator(
            cryptocompare_api_key='some_api_key',
            job_data={'recipients': [{'name': "john"}, {'name': "ben"}, {'name': "lio"}]}
        )
        assert calc._get_variable_costs() == 3

    @mock.patch('cost.models.EthereumCostCalculator._get_eth_gas_station_data', return_value=ETH_GASSTATION_JSON)
    @mock.patch('cost.models.EthereumCostCalculator._get_eth_usd_price', return_value=184.6)
    def test_calculate(self, _, __):
        calc = EthereumCostCalculator(
            cryptocompare_api_key='some_api_key',
            job_data={'recipients': [{'name': "john"}, {'name': "ben"}, {'name': "lio"}]}
        )
        usd_cost = calc.calculate()
        assert usd_cost == 3.004615
