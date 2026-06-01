"""
Alertra - Cross-platform Stock Alert System
Main entry point. Run with: python main.py
"""

import asyncio
import json
import logging
import os
import sys

import flet as ft

from storage.database import Database
from data.provider import get_provider
from indicators import CamarillaIndicator, VolumeSpikeIndicator
from alert.notifier import Notifier
from alert.poller import Poller
from ui.theme import get_theme, glass_container, glass_appbar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Default settings
DEFAULT_SETTINGS = {
    "polling_interval_seconds": "300",
    "cooldown_seconds": "300",
    "volume_multiplier": "3.0",
    "sma_period": "8",
    "theme": "dark",
    "accent_color": "teal",
    "notification_sound": "default",
    "silent_mode_enabled": "false",
    "silent_mode_start": "22:00",
    "silent_mode_end": "07:00",
    "data_provider": "yahoo",
    "api_key": "",
    "market_open": "09:15",
    "market_close": "15:30",
}


class AlertraApp:
    """Main application class."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database(os.path.join(self._get_data_dir(), "alertra.db"))
        self._init_settings()
        self.provider = get_provider(
            self.db.get_setting("data_provider", "yahoo"),
            self.db.get_setting("api_key", ""),
        )
        self.notifier = Notifier("Alertra")
        self.indicators = [CamarillaIndicator(), VolumeSpikeIndicator()]
        self.poller = Poller(
            db=self.db,
            provider=self.provider,
            notifier=self.notifier,
            indicators=self.indicators,
            polling_interval=int(self.db.get_setting("polling_interval_seconds", "300")),
            cooldown_seconds=int(self.db.get_setting("cooldown_seconds", "300")),
        )
        self._setup_page()
        self._build_ui()

    def _get_data_dir(self) -> str:
        """Get application data directory."""
        if sys.platform == "win32":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        else:
            base = os.path.expanduser("~")
        data_dir = os.path.join(base, "Alertra")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir

    def _init_settings(self):
        """Load settings from file into DB if not present."""
        settings_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "settings.json"
        )
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                file_settings = json.load(f)
            for key, value in file_settings.items():
                if self.db.get_setting(key) is None:
                    self.db.set_setting(key, str(value))

        # Ensure all defaults exist
        for key, value in DEFAULT_SETTINGS.items():
            if self.db.get_setting(key) is None:
                self.db.set_setting(key, value)

        # Create default watchlist if none exist
        watchlists = self.db.get_watchlists()
        if not watchlists:
            wl_id = self.db.create_watchlist("My Watchlist")
            self.db.set_active_watchlist(wl_id)

    def _setup_page(self):
        """Configure the Flet page."""
        self.page.title = "Alertra"
        self.page.window.width = 400
        self.page.window.height = 800
        self.page.window.resizable = True
        self.page.padding = 0
        self.page.spacing = 0

        theme_mode = self.db.get_setting("theme", "dark")
        accent = self.db.get_setting("accent_color", "teal")

        if theme_mode == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        elif theme_mode == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM

        self.page.theme = get_theme(accent, "dark")
        self.page.dark_theme = get_theme(accent, "dark")
        self.page.light_theme = get_theme(accent, "light")

    def _build_ui(self):
        """Build the main UI with navigation."""
        # Import screens
        from ui.home_screen import build_home_screen
        from ui.alert_conditions_screen import build_alert_conditions_screen
        from ui.history_screen import build_history_screen
        from ui.settings_screen import build_settings_screen

        self.current_view = "home"

        # Content area
        self.content = ft.Container(expand=True)

        def navigate(view_name: str):
            self.current_view = view_name
            if view_name == "home":
                self.content.content = build_home_screen(
                    self.page, self.db, self.provider,
                    on_navigate=navigate,
                )
            elif view_name == "alerts":
                self.content.content = build_alert_conditions_screen(
                    self.page, self.db, self.indicators,
                )
            elif view_name == "history":
                self.content.content = build_history_screen(
                    self.page, self.db,
                )
            elif view_name == "settings":
                self.content.content = build_settings_screen(
                    self.page, self.db,
                    on_settings_change=self._on_settings_change,
                )
            self.page.update()

        # Bottom navigation
        nav_bar = ft.NavigationBar(
            selected_index=0,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            indicator_color=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icons.DASHBOARD,
                    label="Watchlist",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                    selected_icon=ft.Icons.NOTIFICATIONS,
                    label="Alerts",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.HISTORY_OUTLINED,
                    selected_icon=ft.Icons.HISTORY,
                    label="History",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Settings",
                ),
            ],
            on_change=lambda e: navigate(
                ["home", "alerts", "history", "settings"][e.control.selected_index]
            ),
        )

        # Build layout
        self.page.add(
            ft.Column(
                controls=[
                    self.content,
                    nav_bar,
                ],
                expand=True,
                spacing=0,
            )
        )

        # Start with home screen
        navigate("home")

        # Start poller in background
        self.page.run_task(self._start_poller)

    def _on_settings_change(self):
        """Handle settings changes."""
        self.poller.update_settings(
            polling_interval=int(self.db.get_setting("polling_interval_seconds", "300")),
            cooldown_seconds=int(self.db.get_setting("cooldown_seconds", "300")),
            market_open=self.db.get_setting("market_open", "09:15"),
            market_close=self.db.get_setting("market_close", "15:30"),
        )

        # Update theme
        theme_mode = self.db.get_setting("theme", "dark")
        if theme_mode == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        elif theme_mode == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM

        accent = self.db.get_setting("accent_color", "teal")
        self.page.theme = get_theme(accent, "dark")
        self.page.dark_theme = get_theme(accent, "dark")
        self.page.light_theme = get_theme(accent, "light")
        self.page.update()

    async def _start_poller(self):
        """Start the background poller."""
        try:
            await self.poller.start()
        except Exception as e:
            logger.error(f"Poller error: {e}")


def main(page: ft.Page):
    """Flet app entry point."""
    AlertraApp(page)


if __name__ == "__main__":
    ft.app(target=main)
