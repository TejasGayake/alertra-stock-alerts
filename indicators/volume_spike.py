from typing import Tuple, Dict, Any, List
from .base import Indicator


class VolumeSpikeIndicator(Indicator):
    name = "volume_spike"
    description = "Volume spike detector using SMA of volume"
    default_params: Dict[str, Any] = {
        "multiplier": 3.0,
        "sma_period": 8,
    }

    def cooldown_key(self, symbol: str) -> str:
        return f"volume_spike:{symbol}"

    def evaluate(self, data: dict, params: dict) -> Tuple[bool, str]:
        """
        Evaluate volume spike conditions.

        Expected data keys:
            - symbol: str
            - current_volume: float
            - volume_history: List[float] (recent volume values, oldest first)
        """
        merged = {**self.default_params, **params}
        multiplier: float = merged["multiplier"]
        sma_period: int = merged["sma_period"]

        symbol = data["symbol"]
        current_volume: float = data["current_volume"]
        volume_history: List[float] = data["volume_history"]

        recent = volume_history[-sma_period:]
        if len(recent) < sma_period:
            return False, ""

        sma_vol = sum(recent) / sma_period

        if current_volume > multiplier * sma_vol:
            ratio = current_volume / sma_vol
            msg = (
                f"Volume Spike: {symbol} volume ({current_volume:,.0f}) "
                f"is {ratio:.1f}x above SMA{sma_period} ({sma_vol:,.0f})"
            )
            return True, msg

        return False, ""
