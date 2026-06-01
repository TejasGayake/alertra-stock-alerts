"""Settings screen for Alertra."""

import flet as ft


def _glass_card(content: ft.Control, **kwargs) -> ft.Container:
    """Wrap content in a liquid-glass styled container."""
    defaults = dict(
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        border_radius=24,
        border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
        blur=ft.Blur(10, 10, ft.BlurMode.NORMAL),
        padding=16,
        margin=ft.margin.only(bottom=8),
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )
    defaults.update(kwargs)
    return ft.Container(content=content, **defaults)


def _section_header(title: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(
            title,
            size=14,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.TEAL_200,
        ),
        padding=ft.padding.only(left=4, top=16, bottom=6),
    )


def _setting_row(label: str, control: ft.Control) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    label,
                    size=14,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.W_400,
                    expand=True,
                ),
                control,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(vertical=6),
    )


def build_settings_screen(
    page: ft.Page,
    db,
    on_settings_change=None,
    on_navigate=None,
) -> ft.Control:
    """Build the settings screen with all configuration sections."""

    all_settings = db.get_all_settings()

    def _get(key: str, default: str = "") -> str:
        return all_settings.get(key, default)

    # -- Header --
    def go_back(e):
        if on_navigate:
            on_navigate("home")

    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                    icon_color=ft.Colors.WHITE,
                    icon_size=22,
                    on_click=go_back,
                ),
                ft.Text(
                    "Settings",
                    size=22,
                    weight=ft.FontWeight.W_700,
                    color=ft.Colors.WHITE,
                ),
                ft.Container(width=48),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(left=4, right=12, top=12, bottom=4),
    )

    # ----------------------------------------------------------------
    # GENERAL
    # ----------------------------------------------------------------
    polling_val = float(_get("polling_interval", "60"))
    polling_slider = ft.Slider(
        min=30,
        max=600,
        value=polling_val,
        divisions=19,
        label="{value}s",
        active_color=ft.Colors.TEAL,
        inactive_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
    )

    def _save_polling(e):
        db.set_setting("polling_interval", str(int(polling_slider.value)))
        if on_settings_change:
            on_settings_change("polling_interval", str(int(polling_slider.value)))

    polling_slider.on_change_end = _save_polling

    cooldown_val = float(_get("cooldown_minutes", "5"))
    cooldown_slider = ft.Slider(
        min=1,
        max=15,
        value=cooldown_val,
        divisions=14,
        label="{value} min",
        active_color=ft.Colors.TEAL,
        inactive_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
    )

    def _save_cooldown(e):
        db.set_setting("cooldown_minutes", str(int(cooldown_slider.value)))
        if on_settings_change:
            on_settings_change("cooldown_minutes", str(int(cooldown_slider.value)))

    cooldown_slider.on_change_end = _save_cooldown

    theme_dd = ft.Dropdown(
        value=_get("theme", "dark"),
        options=[
            ft.dropdown.Option("dark", "Dark"),
            ft.dropdown.Option("light", "Light"),
            ft.dropdown.Option("system", "System"),
        ],
        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        border_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
        border_radius=12,
        text_style=ft.TextStyle(color=ft.Colors.WHITE, size=14),
        content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
        width=140,
        dense=True,
    )

    def _save_theme(e):
        db.set_setting("theme", theme_dd.value)
        if on_settings_change:
            on_settings_change("theme", theme_dd.value)

    theme_dd.on_change = _save_theme

    general_card = _glass_card(
        ft.Column(
            [
                _setting_row("Polling Interval", ft.Text(f"{int(polling_val)}s", size=13, color=ft.Colors.WHITE54)),
                polling_slider,
                ft.Divider(height=8, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                _setting_row("Alert Cooldown", ft.Text(f"{int(cooldown_val)} min", size=13, color=ft.Colors.WHITE54)),
                cooldown_slider,
                ft.Divider(height=8, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                _setting_row("Theme", theme_dd),
            ],
            spacing=0,
        ),
    )

    # ----------------------------------------------------------------
    # NOTIFICATIONS
    # ----------------------------------------------------------------
    silent_mode = ft.Switch(
        value=_get("silent_mode", "false").lower() == "true",
        active_color=ft.Colors.TEAL,
        active_track_color=ft.Colors.with_opacity(0.4, ft.Colors.TEAL),
    )

    def _save_silent(e):
        db.set_setting("silent_mode", "true" if silent_mode.value else "false")
        if on_settings_change:
            on_settings_change("silent_mode", str(silent_mode.value).lower())

    silent_mode.on_change = _save_silent

    silent_start = _get("silent_start", "22:00")
    silent_end = _get("silent_end", "07:00")

    start_time_btn = ft.ElevatedButton(
        silent_start,
        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        ),
    )

    end_time_btn = ft.ElevatedButton(
        silent_end,
        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        ),
    )

    def _pick_time(target_btn: ft.ElevatedButton, setting_key: str):
        def handler(e):
            tp = ft.TimePicker(
                confirm_text="OK",
                cancel_text="Cancel",
                time_picker_entry_mode=ft.TimePickerEntryMode.INPUT,
            )

            def on_change(ev):
                if ev.data:
                    # TimePicker returns "HH:MM:SS" or "HH:MM"
                    parts = ev.data.split(":")
                    formatted = f"{parts[0]}:{parts[1]}"
                    target_btn.text = formatted
                    db.set_setting(setting_key, formatted)
                    if on_settings_change:
                        on_settings_change(setting_key, formatted)
                    page.update()

            tp.on_change = on_change
            page.open(tp)

        return handler

    start_time_btn.on_click = _pick_time(start_time_btn, "silent_start")
    end_time_btn.on_click = _pick_time(end_time_btn, "silent_end")

    notifications_card = _glass_card(
        ft.Column(
            [
                _setting_row("Silent Mode", silent_mode),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("Start", size=12, color=ft.Colors.WHITE54),
                                    start_time_btn,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=4,
                            ),
                            ft.Text("--", size=16, color=ft.Colors.WHITE38),
                            ft.Column(
                                [
                                    ft.Text("End", size=12, color=ft.Colors.WHITE54),
                                    end_time_btn,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=4,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    padding=ft.padding.only(top=8),
                ),
            ],
            spacing=4,
        ),
    )

    # ----------------------------------------------------------------
    # DATA / PROVIDER
    # ----------------------------------------------------------------
    provider_dd = ft.Dropdown(
        value=_get("api_provider", "yahoo"),
        options=[
            ft.dropdown.Option("yahoo", "Yahoo Finance"),
            ft.dropdown.Option("polygon", "Polygon.io"),
            ft.dropdown.Option("twelvedata", "TwelveData"),
        ],
        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        border_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
        border_radius=12,
        text_style=ft.TextStyle(color=ft.Colors.WHITE, size=14),
        content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
        dense=True,
    )

    def _save_provider(e):
        db.set_setting("api_provider", provider_dd.value)
        if on_settings_change:
            on_settings_change("api_provider", provider_dd.value)

    provider_dd.on_change = _save_provider

    api_key_field = ft.TextField(
        value=_get("api_key", ""),
        hint_text="Enter API key (optional)",
        hint_style=ft.TextStyle(color=ft.Colors.WHITE38, size=13),
        text_style=ft.TextStyle(color=ft.Colors.WHITE, size=14),
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        border_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
        border_radius=12,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        password=True,
        can_reveal_password=True,
        dense=True,
    )

    def _save_api_key(e):
        db.set_setting("api_key", api_key_field.value)
        if on_settings_change:
            on_settings_change("api_key", api_key_field.value)

    api_key_field.on_blur = _save_api_key

    data_card = _glass_card(
        ft.Column(
            [
                _setting_row("Data Provider", ft.Container()),
                provider_dd,
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "API Key",
                                size=13,
                                color=ft.Colors.WHITE70,
                            ),
                            api_key_field,
                        ],
                        spacing=4,
                    ),
                    padding=ft.padding.only(top=8),
                ),
            ],
            spacing=4,
        ),
    )

    # ----------------------------------------------------------------
    # ABOUT
    # ----------------------------------------------------------------
    about_card = _glass_card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SHIELD_ROUNDED, color=ft.Colors.TEAL, size=28),
                        ft.Column(
                            [
                                ft.Text(
                                    "Alertra",
                                    size=18,
                                    weight=ft.FontWeight.W_700,
                                    color=ft.Colors.WHITE,
                                ),
                                ft.Text(
                                    "v1.0.0",
                                    size=13,
                                    color=ft.Colors.WHITE54,
                                ),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=ft.Text(
                        "Real-time stock alert monitoring with intelligent indicators.",
                        size=13,
                        color=ft.Colors.WHITE54,
                    ),
                    padding=ft.padding.only(top=8),
                ),
            ],
            spacing=4,
        ),
    )

    # -- Assemble all sections --
    body = ft.Column(
        [
            header,
            ft.Container(
                content=ft.Column(
                    [
                        _section_header("General"),
                        general_card,
                        _section_header("Notifications"),
                        notifications_card,
                        _section_header("Data"),
                        data_card,
                        _section_header("About"),
                        about_card,
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
                padding=ft.padding.symmetric(horizontal=16),
            ),
        ],
        spacing=0,
        expand=True,
    )

    return body
