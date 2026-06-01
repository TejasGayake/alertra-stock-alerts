from typing import Tuple, Dict, Any
from .base import Indicator


class CamarillaIndicator(Indicator):
    name = "camarilla"
    description = "Camarilla Pivot Points H4/L4 breakout detector"
    default_params: Dict[str, Any] = {}

    def cooldown_key(self, symbol: str) -> str:
        return f"camarilla:{symbol}"

    def evaluate(self, data: dict, params: dict) -> Tuple[bool, str]:
        """
        Evaluate Camarilla breakout conditions.

        Expected data keys:
            - symbol: str
            - high: float (previous day high)
            - low: float (previous day low)
            - close: float (previous day close)
            - current_price: float
        """
        symbol = data["symbol"]
        high = data["high"]
        low = data["low"]
        close = data["close"]
        current_price = data["current_price"]

        range_hl = high - low
        h4 = close + (range_hl * 1.1) / 2
        l4 = close - (range_hl * 1.1) / 2

        if current_price > h4:
            msg = (
                f"Camarilla Bullish Breakout: {symbol} at {current_price} "
                f"broke above H4 ({h4:.2f})"
            )
            return True, msg

        if current_price < l4:
            msg = (
                f"Camarilla Bearish Breakout: {symbol} at {current_price} "
                f"broke below L4 ({l4:.2f})"
            )
            return True, msg

        return False, ""
