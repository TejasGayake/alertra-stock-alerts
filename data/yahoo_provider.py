"""Yahoo Finance data provider implementation for the Alertra stock alert app."""

import asyncio
import logging
import time
from typing import Optional

import yfinance as yf

from .provider import DataProvider

logger = logging.getLogger(__name__)

# Cache TTL constants (seconds)
PRICE_TTL = 60
HISTORICAL_TTL = 300

# Common stocks for fuzzy search fallback
_POPULAR_STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
    {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"},
    {"symbol": "NFLX", "name": "Netflix Inc.", "exchange": "NASDAQ"},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE"},
    {"symbol": "V", "name": "Visa Inc.", "exchange": "NYSE"},
    {"symbol": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE"},
    {"symbol": "WMT", "name": "Walmart Inc.", "exchange": "NYSE"},
    {"symbol": "PG", "name": "Procter & Gamble Co.", "exchange": "NYSE"},
    {"symbol": "MA", "name": "Mastercard Inc.", "exchange": "NYSE"},
    {"symbol": "DIS", "name": "Walt Disney Co.", "exchange": "NYSE"},
    {"symbol": "BAC", "name": "Bank of America Corp.", "exchange": "NYSE"},
    {"symbol": "XOM", "name": "Exxon Mobil Corp.", "exchange": "NYSE"},
    {"symbol": "AMD", "name": "Advanced Micro Devices Inc.", "exchange": "NASDAQ"},
    {"symbol": "INTC", "name": "Intel Corporation", "exchange": "NASDAQ"},
    {"symbol": "CRM", "name": "Salesforce Inc.", "exchange": "NYSE"},
    {"symbol": "PYPL", "name": "PayPal Holdings Inc.", "exchange": "NASDAQ"},
    {"symbol": "UBER", "name": "Uber Technologies Inc.", "exchange": "NYSE"},
    {"symbol": "SQ", "name": "Block Inc.", "exchange": "NYSE"},
    {"symbol": "SPOT", "name": "Spotify Technology S.A.", "exchange": "NYSE"},
    {"symbol": "COIN", "name": "Coinbase Global Inc.", "exchange": "NASDAQ"},
    {"symbol": "PLTR", "name": "Palantir Technologies Inc.", "exchange": "NYSE"},
    {"symbol": "SOFI", "name": "SoFi Technologies Inc.", "exchange": "NASDAQ"},
    {"symbol": "NIO", "name": "NIO Inc.", "exchange": "NYSE"},
    {"symbol": "RIVN", "name": "Rivian Automotive Inc.", "exchange": "NASDAQ"},
    {"symbol": "LCID", "name": "Lucid Group Inc.", "exchange": "NASDAQ"},
    {"symbol": "SNAP", "name": "Snap Inc.", "exchange": "NYSE"},
    {"symbol": "PINS", "name": "Pinterest Inc.", "exchange": "NYSE"},
    {"symbol": "ROKU", "name": "Roku Inc.", "exchange": "NASDAQ"},
    {"symbol": "ZM", "name": "Zoom Video Communications Inc.", "exchange": "NASDAQ"},
    {"symbol": "ABNB", "name": "Airbnb Inc.", "exchange": "NASDAQ"},
    {"symbol": "DASH", "name": "DoorDash Inc.", "exchange": "NYSE"},
    {"symbol": "SHOP", "name": "Shopify Inc.", "exchange": "NYSE"},
    {"symbol": "SQ", "name": "Block Inc.", "exchange": "NYSE"},
    {"symbol": "BA", "name": "Boeing Co.", "exchange": "NYSE"},
    {"symbol": "KO", "name": "Coca-Cola Co.", "exchange": "NYSE"},
    {"symbol": "PEP", "name": "PepsiCo Inc.", "exchange": "NASDAQ"},
    {"symbol": "COST", "name": "Costco Wholesale Corp.", "exchange": "NASDAQ"},
    {"symbol": "HD", "name": "Home Depot Inc.", "exchange": "NYSE"},
    {"symbol": "MCD", "name": "McDonald's Corp.", "exchange": "NYSE"},
    {"symbol": "NKE", "name": "Nike Inc.", "exchange": "NYSE"},
    {"symbol": "SBUX", "name": "Starbucks Corp.", "exchange": "NASDAQ"},
    {"symbol": "T", "name": "AT&T Inc.", "exchange": "NYSE"},
    {"symbol": "VZ", "name": "Verizon Communications Inc.", "exchange": "NYSE"},
    {"symbol": "INTC", "name": "Intel Corporation", "exchange": "NASDAQ"},
    {"symbol": "CSCO", "name": "Cisco Systems Inc.", "exchange": "NASDAQ"},
    {"symbol": "ORCL", "name": "Oracle Corp.", "exchange": "NYSE"},
    {"symbol": "IBM", "name": "International Business Machines Corp.", "exchange": "NYSE"},
]


class _CacheEntry:
    """Simple cache entry with TTL."""

    __slots__ = ("data", "timestamp", "ttl")

    def __init__(self, data, ttl: float):
        self.data = data
        self.timestamp = time.monotonic()
        self.ttl = ttl

    def is_valid(self) -> bool:
        return (time.monotonic() - self.timestamp) < self.ttl


class YahooDataProvider(DataProvider):
    """Yahoo Finance data provider using the yfinance library."""

    def __init__(self):
        self._cache: dict[str, _CacheEntry] = {}

    def _get_cached(self, key: str):
        """Return cached data if still valid, else None."""
        entry = self._cache.get(key)
        if entry and entry.is_valid():
            return entry.data
        return None

    def _set_cache(self, key: str, data, ttl: float):
        """Store data in cache with the given TTL."""
        self._cache[key] = _CacheEntry(data, ttl)

    async def get_current_price(self, symbol: str) -> Optional[dict]:
        """Get current price and daily change percentage from Yahoo Finance."""
        cache_key = f"price:{symbol}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            ticker = yf.Ticker(symbol)
            info = await asyncio.to_thread(lambda: ticker.info)

            if not info or "currentPrice" not in info:
                # Fallback: try fast_info or previousClose-based calc
                fast = await asyncio.to_thread(lambda: ticker.fast_info)
                price = getattr(fast, "last_price", None)
                prev_close = getattr(fast, "previous_close", None)
                if price is None:
                    logger.warning("No price data for %s", symbol)
                    return None
                change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0
            else:
                price = float(info["currentPrice"])
                prev_close = info.get("previousClose", price)
                change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0

            result = {"price": round(price, 2), "change_pct": round(change_pct, 2)}
            self._set_cache(cache_key, result, PRICE_TTL)
            return result

        except Exception as e:
            logger.error("Failed to get current price for %s: %s", symbol, e)
            return None

    async def get_camarilla_data(self, symbol: str) -> Optional[dict]:
        """Get previous day high, low, close and current price for Camarilla pivots."""
        cache_key = f"camarilla:{symbol}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            ticker = yf.Ticker(symbol)

            # Get 2 days of daily history to ensure we have the previous trading day
            hist = await asyncio.to_thread(lambda: ticker.history(period="5d", interval="1d"))

            if hist.empty or len(hist) < 1:
                logger.warning("No history data for %s", symbol)
                return None

            # Use the last complete day for H/L/C
            last_day = hist.iloc[-1]
            high = float(last_day["High"])
            low = float(last_day["Low"])
            close = float(last_day["Close"])

            # Get current price
            price_data = await self.get_current_price(symbol)
            current_price = price_data["price"] if price_data else close

            result = {
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "current_price": round(current_price, 2),
            }
            self._set_cache(cache_key, result, HISTORICAL_TTL)
            return result

        except Exception as e:
            logger.error("Failed to get camarilla data for %s: %s", symbol, e)
            return None

    async def get_volume_data(self, symbol: str, period: int = 8) -> Optional[dict]:
        """Get recent volume data. Tries 5-minute candles first, falls back to daily."""
        cache_key = f"volume:{symbol}:{period}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            ticker = yf.Ticker(symbol)
            volumes: list[float] = []

            # Try 5-minute intraday data first
            try:
                hist = await asyncio.to_thread(
                    lambda: ticker.history(period="1d", interval="5m")
                )
                if not hist.empty and len(hist) >= 2:
                    volumes = [float(v) for v in hist["Volume"].tail(period).tolist()]
            except Exception:
                pass

            # Fallback to daily data if intraday unavailable or too few bars
            if len(volumes) < 2:
                hist = await asyncio.to_thread(
                    lambda: ticker.history(period="1mo", interval="1d")
                )
                if hist.empty:
                    logger.warning("No volume data for %s", symbol)
                    return None
                volumes = [float(v) for v in hist["Volume"].tail(period).tolist()]

            current_volume = volumes[-1] if volumes else 0.0

            result = {
                "current_volume": round(current_volume, 0),
                "volumes": [round(v, 0) for v in volumes],
            }
            self._set_cache(cache_key, result, HISTORICAL_TTL)
            return result

        except Exception as e:
            logger.error("Failed to get volume data for %s: %s", symbol, e)
            return None

    async def get_quote(self, symbol: str) -> Optional[dict]:
        """Get full quote information for a symbol."""
        cache_key = f"quote:{symbol}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            ticker = yf.Ticker(symbol)
            info = await asyncio.to_thread(lambda: ticker.info)

            if not info or "symbol" not in info:
                logger.warning("No quote info for %s", symbol)
                return None

            price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            prev_close = info.get("previousClose", price)
            change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0

            result = {
                "symbol": info.get("symbol", symbol.upper()),
                "price": round(float(price), 2),
                "change_pct": round(change_pct, 2),
                "volume": float(info.get("volume", 0)),
                "name": info.get("shortName", info.get("longName", symbol)),
            }
            self._set_cache(cache_key, result, PRICE_TTL)
            return result

        except Exception as e:
            logger.error("Failed to get quote for %s: %s", symbol, e)
            return None

    async def search_symbols(self, query: str) -> list[dict]:
        """Search for symbols matching a query. Uses yfinance search with fuzzy fallback."""
        if not query or len(query.strip()) < 1:
            return []

        query_lower = query.strip().lower()

        try:
            # Try yfinance's built-in search
            results = await asyncio.to_thread(yf.search, query)
            quotes = results.get("quotes", []) if results else []

            if quotes:
                matches = []
                for q in quotes[:10]:
                    symbol = q.get("symbol", "")
                    if not symbol:
                        continue
                    matches.append({
                        "symbol": symbol,
                        "name": q.get("shortname", q.get("longname", symbol)),
                        "exchange": q.get("exchange", "Unknown"),
                    })
                return matches

        except Exception as e:
            logger.debug("yfinance search failed for '%s': %s", query, e)

        # Fuzzy fallback on popular stocks
        matches = []
        for stock in _POPULAR_STOCKS:
            if (query_lower in stock["symbol"].lower()
                    or query_lower in stock["name"].lower()):
                matches.append(stock)

        # Deduplicate by symbol
        seen = set()
        unique = []
        for m in matches:
            if m["symbol"] not in seen:
                seen.add(m["symbol"])
                unique.append(m)

        return unique[:10]
