"""
Cross-platform notification system for Alertra.
Uses plyer for native notifications on Windows and Android.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Notifier:
    """Handles sending cross-platform notifications."""

    def __init__(self, app_name: str = "Alertra"):
        self.app_name = app_name
        self._enabled = True
        self._sound_enabled = True
        self._silent_mode = False
        self._silent_start = "22:00"
        self._silent_end = "07:00"

    def configure(
        self,
        enabled: bool = True,
        sound_enabled: bool = True,
        silent_mode: bool = False,
        silent_start: str = "22:00",
        silent_end: str = "07:00",
    ):
        self._enabled = enabled
        self._sound_enabled = sound_enabled
        self._silent_mode = silent_mode
        self._silent_start = silent_start
        self._silent_end = silent_end

    def _is_silent_time(self) -> bool:
        """Check if current time is within silent mode window."""
        if not self._silent_mode:
            return False
        from datetime import datetime

        now = datetime.now().time()
        start = datetime.strptime(self._silent_start, "%H:%M").time()
        end = datetime.strptime(self._silent_end, "%H:%M").time()
        if start <= end:
            return start <= now <= end
        return now >= start or now <= end

    def send(self, title: str, message: str, priority: str = "normal") -> bool:
        """
        Send a notification.
        Returns True if notification was sent, False if suppressed.
        """
        if not self._enabled:
            logger.debug("Notifications disabled, skipping")
            return False

        if self._is_silent_time():
            logger.debug("Silent mode active, skipping notification")
            return False

        try:
            from plyer import notification

            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                timeout=10,
            )
            logger.info(f"Notification sent: {title} - {message}")
            return True
        except ImportError:
            logger.warning("plyer not available, using fallback print notification")
            print(f"\n{'='*50}")
            print(f"ALERT: {title}")
            print(f"{message}")
            print(f"{'='*50}\n")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            print(f"\n[ALERT] {title}: {message}")
            return False

    def send_alert(
        self,
        symbol: str,
        condition: str,
        price: float,
        message: str,
    ) -> bool:
        """Send a stock alert notification."""
        title = f"{symbol} - {condition}"
        body = f"{message}\nPrice: {price:.2f}"
        return self.send(title, body)

    def test_notification(self) -> bool:
        """Send a test notification."""
        return self.send(
            title="Alertra Test",
            message="Notifications are working!",
        )
