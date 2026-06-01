"""Base data provider and factory for the Alertra stock alert app."""

from abc import ABC, abstractmethod
from typing import Optional


class DataProvider(ABC):
    """Base class for data providers. All providers must implement these methods."""

    @abstractmethod
    async def get_current_price(self, symbol: str) -> Optional[dict]:
        """Get current price and daily change percentage.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            {"price": float, "change_pct": float} or None on failure
        """
        pass

    @abstractmethod
    async def get_camarilla_data(self, symbol: str) -> Optional[dict]:
        """Get Camarilla pivot data (previous day high/low/close + current price).

        Args:
            symbol: Stock ticker symbol

        Returns:
            {"high": float, "low": float, "close": float, "current_price": float} or None on failure
        """
        pass

    @abstractmethod
    async def get_volume_data(self, symbol: str, period: int = 8) -> Optional[dict]:
        """Get volume data for the given symbol.

        Args:
            symbol: Stock ticker symbol
            period: Number of recent volume values to return

        Returns:
            {"current_volume": float, "volumes": list[float]} or None on failure
        """
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> Optional[dict]:
        """Get full quote information for a symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            {"symbol": str, "price": float, "change_pct": float, "volume": float, "name": str}
            or None on failure
        """
        pass

    @abstractmethod
    async def search_symbols(self, query: str) -> list[dict]:
        """Search for symbols matching a query string.

        Args:
            query: Search query (company name or symbol)

        Returns:
            List of {"symbol": str, "name": str, "exchange": str}
        """
        pass


def get_provider(provider_name: str = "yahoo", api_key: str = "") -> DataProvider:
    """Factory function to get a data provider instance.

    Args:
        provider_name: Name of the provider ('yahoo')
        api_key: Optional API key (unused for Yahoo)

    Returns:
        DataProvider instance

    Raises:
        ValueError: If provider_name is unknown
    """
    if provider_name == "yahoo":
        from .yahoo_provider import YahooDataProvider
        return YahooDataProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}. Available providers: yahoo")
