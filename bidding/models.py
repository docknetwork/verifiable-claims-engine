from abc import abstractmethod, ABC

from cost.models import CostCalculator


class BidCalculator(ABC):
    """Abstract class to implement bid calculators for different scenarios."""

    def __init__(self, cost_calculator: CostCalculator, roi_factor: int):
        self.cost_calculator = cost_calculator
        self.roi_factor = roi_factor

    @abstractmethod
    def calculate(self) -> float:
        """Calculate bid in USD."""
        pass


class SampleBidCalculator(BidCalculator):

    def calculate(self) -> float:
        return self.roi_factor * self.cost_calculator.calculate()
