from unittest import mock

from bidding.models import SampleBidCalculator
from cost.models import EthereumCostCalculator


class TestSampleBidding:

    @mock.patch('cost.models.EthereumCostCalculator.calculate', return_value=50)
    def test_calculate(self, _):
        cost_calculator = EthereumCostCalculator(
            cryptocompare_api_key='some_api_key',
            job_data={'recipients': [{'name': "john"}, {'name': "ben"}, {'name': "lio"}]}
        )
        bid_calculator_x5000 = SampleBidCalculator(
            cost_calculator=cost_calculator,
            roi_factor=5000,
        )
        assert bid_calculator_x5000.calculate() == cost_calculator.calculate() * 5000
