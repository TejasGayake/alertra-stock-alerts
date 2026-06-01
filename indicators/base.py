from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any


class Indicator(ABC):
    name: str
    description: str
    default_params: Dict[str, Any]

    @abstractmethod
    def cooldown_key(self, symbol: str) -> str:
        """Return unique key for cooldown tracking"""
        pass

    @abstractmethod
    def evaluate(self, data: dict, params: dict) -> Tuple[bool, str]:
        """
        Evaluate the indicator.
        Returns: (triggered: bool, message: str)
        """
        pass
