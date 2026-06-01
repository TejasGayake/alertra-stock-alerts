"""
Async polling engine for Alertra.
Periodically checks watchlist symbols against enabled indicators.
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class Poller:
    """Async polling loop that checks indicators and triggers alerts."""

    def __init__(
        self,
        db,
        provider,
        notifier,
        indicators: list,
        polling_interval: int = 300,
        cooldown_seconds: int = 300,
    ):
        self.db = db
        self.provider = provider
        self.notifier = notifier
        self.indicators = indicators
        self.polling_interval = polling_interval
        self.cooldown_seconds = cooldown_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._force_update = False
        self._market_open = time(9, 15)
        self._market_close = time(15, 30)
        self._skip_market_check = True  # Allow polling outside market hours for testing
        self._on_alert_callback: Optional[Callable] = None

    def set_alert_callback(self, callback: Callable):
        """Set callback for when alert is triggered (for UI updates)."""
        self._on_alert_callback = callback

    def _is_market_hours(self) -> bool:
        """Check if current time is within market hours."""
        now = datetime.now().time()
        return self._market_open <= now <= self._market_close

    def update_settings(
        self,
        polling_interval: int = None,
        cooldown_seconds: int = None,
        market_open: str = None,
        market_close: str = None,
    ):
        """Update polling settings dynamically."""
        if polling_interval is not None:
            self.polling_interval = polling_interval
        if cooldown_seconds is not None:
            self.cooldown_seconds = cooldown_seconds
        if market_open:
            parts = market_open.split(":")
            self._market_open = time(int(parts[0]), int(parts[1]))
        if market_close:
            parts = market_close.split(":")
            self._market_close = time(int(parts[0]), int(parts[1]))

    def force_update(self):
        """Trigger an immediate poll outside the regular interval."""
        self._force_update = True

    async def _check_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """Check all enabled indicators for a single symbol."""
        alerts = []

        try:
            for indicator in self.indicators:
                indicator_name = indicator.name

                # Get required data based on indicator
                if indicator_name == "camarilla":
                    data = await self.provider.get_camarilla_data(symbol)
                    if data:
                        data["symbol"] = symbol
                elif indicator_name == "volume_spike":
                    data = await self.provider.get_volume_data(symbol)
                    if data:
                        data["symbol"] = symbol
                        data["volume_history"] = data.pop("volumes", [])
                else:
                    data = await self.provider.get_current_price(symbol)
                    if data:
                        data["symbol"] = symbol

                if data is None:
                    logger.warning(f"No data for {symbol} ({indicator_name})")
                    continue

                # Get indicator params from settings
                params = indicator.default_params.copy()
                if indicator_name == "volume_spike":
                    stored_mult = self.db.get_setting("volume_multiplier")
                    if stored_mult:
                        params["multiplier"] = float(stored_mult)
                    stored_period = self.db.get_setting("sma_period")
                    if stored_period:
                        params["sma_period"] = int(stored_period)

                # Evaluate indicator
                triggered, message = indicator.evaluate(data, params)

                if triggered:
                    # Check cooldown
                    if self.db.is_in_cooldown(symbol, indicator_name, self.cooldown_seconds):
                        logger.debug(f"{symbol} {indicator_name} in cooldown")
                        continue

                    # Get current price for alert record
                    price = data.get("current_price") or data.get("price", 0.0)

                    # Save alert to DB
                    self.db.save_alert(symbol, indicator_name, price, message)
                    self.db.update_cooldown(symbol, indicator_name)

                    # Send notification
                    self.notifier.send_alert(
                        symbol=symbol,
                        condition=indicator_name,
                        price=price,
                        message=message,
                    )

                    alerts.append({
                        "symbol": symbol,
                        "condition": indicator_name,
                        "price": price,
                        "message": message,
                    })

                    logger.info(f"Alert triggered: {symbol} - {indicator_name}")

        except Exception as e:
            logger.error(f"Error checking {symbol}: {e}")

        return alerts

    async def _poll_cycle(self) -> List[Dict[str, Any]]:
        """Run one complete poll cycle across all watchlist symbols."""
        all_alerts = []

        # Get active watchlist symbols
        active_wl = self.db.get_active_watchlist()
        if not active_wl:
            watchlists = self.db.get_watchlists()
            if watchlists:
                active_wl = watchlists[0]
                self.db.set_active_watchlist(active_wl["id"])
            else:
                logger.debug("No watchlists found, skipping poll")
                return all_alerts

        symbols = self.db.get_symbols(active_wl["id"])
        if not symbols:
            logger.debug("No symbols in watchlist, skipping poll")
            return all_alerts

        logger.info(f"Polling {len(symbols)} symbols...")

        for item in symbols:
            symbol = item["symbol"]
            alerts = await self._check_symbol(symbol)
            all_alerts.extend(alerts)
            await asyncio.sleep(0.5)  # Small delay between symbols

        return all_alerts

    async def start(self):
        """Start the polling loop."""
        if self._running:
            logger.warning("Poller already running")
            return

        self._running = True
        logger.info(f"Poller started (interval: {self.polling_interval}s)")

        while self._running:
            try:
                # Check if we should poll
                should_poll = self._force_update or self._skip_market_check or self._is_market_hours()

                if should_poll:
                    self._force_update = False
                    alerts = await self._poll_cycle()

                    if alerts and self._on_alert_callback:
                        try:
                            self._on_alert_callback(alerts)
                        except Exception as e:
                            logger.error(f"Alert callback error: {e}")
                else:
                    logger.debug("Outside market hours, skipping poll")

            except Exception as e:
                logger.error(f"Poll cycle error: {e}")

            # Wait for next cycle
            await asyncio.sleep(self.polling_interval)

    async def stop(self):
        """Stop the polling loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Poller stopped")
