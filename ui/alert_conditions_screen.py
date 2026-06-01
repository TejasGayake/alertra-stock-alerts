"""Alert conditions configuration screen for Alertra."""

import flet as ft
from ui.theme import border_all


def _glass_card(content: ft.Control, **kwargs) -> ft.Container:
    """Wrap content in a liquid-glass styled container."""
    defaults = dict(
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        border_radius=24,
        border=border_all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
        blur=ft.Blur(10, 10, ft.BlurMode.NORMAL),
        padding=16,
        margin=ft.margin.Margin(left=0, top=0, right=0, bottom=8),
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )
    defaults.update(kwargs)
    return ft.Container(content=content, **defaults)


def _param_editor_sheet(page: ft.Page, indicator, current_params: dict, on_save) -> ft.BottomSheet:
    """Build a bottom-sheet parameter editor for a single indicator."""
    param_controls = []
    edited = dict(current_params)

    for key, default_val in indicator.default_params.items():
        current_val = float(edited.get(key, default_val))

        if isinstance(default_val, float):
            slider = ft.Slider(
                min=1.0,
                max=10.0,
                value=current_val,
                divisions=18,
                label="{value:.1f}",
                active_color=ft.Colors.TEAL,
                inactive_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            )

            def _make_on_change(k, s):
                def handler(e):
                    edited[k] = round(s.value, 1)
                return handler

            slider.on_change_end = _make_on_change(key, slider)

            param_controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                key.replace("_", " ").title(),
                                size=13,
                                color=ft.Colors.WHITE70,
                                weight=ft.FontWeight.W_500,
                            ),
                            slider,
                        ],
                        spacing=4,
                    ),
                    padding=ft.padding.Padding(left=0, top=0, right=0, bottom=12),
                )
            )
        elif isinstance(default_val, int):
            slider = ft.Slider(
                min=2,
                max=30,
                value=current_val,
                divisions=28,
                label="{value}",
                active_color=ft.Colors.TEAL,
                inactive_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            )

            def _make_on_change_int(k, s):
                def handler(e):
                    edited[k] = int(s.value)
                return handler

            slider.on_change_end = _make_on_change_int(key, slider)

            param_controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                key.replace("_", " ").title(),
                                size=13,
                                color=ft.Colors.WHITE70,
                                weight=ft.FontWeight.W_500,
                            ),
                            slider,
                        ],
                        spacing=4,
                    ),
                    padding=ft.padding.Padding(left=0, top=0, right=0, bottom=12),
                )
            )

    def _save(e):
        on_save(edited)
        page.close(sheet)

    def _cancel(e):
        page.close(sheet)

    sheet_content = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                indicator.name.replace("_", " ").title(),
                                size=20,
                                weight=ft.FontWeight.W_700,
                                color=ft.Colors.WHITE,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE_ROUNDED,
                                icon_color=ft.Colors.WHITE54,
                                on_click=_cancel,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.Padding(left=0, top=0, right=0, bottom=8),
                ),
                ft.Text(
                    indicator.description,
                    size=13,
                    color=ft.Colors.WHITE54,
                ),
                ft.Divider(color=ft.Colors.with_opacity(0.15, ft.Colors.WHITE), height=16),
                *param_controls,
                ft.Container(
                    content=ft.ElevatedButton(
                        "Save Parameters",
                        bgcolor=ft.Colors.TEAL,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=16),
                            padding=ft.padding.Padding(left=24, top=14, right=24, bottom=14),
                        ),
                        on_click=_save,
                    ),
                    padding=ft.padding.Padding(left=0, top=12, right=0, bottom=0),
                    alignment=ft.alignment.Alignment(0, 0),
                ),
            ],
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.Padding(left=24, top=24, right=24, bottom=24),
        bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.GREY_900),
        border_radius=ft.border_radius.BorderRadius(top_left=24, top_right=24, bottom_left=0, bottom_right=0),
    )

    sheet = ft.BottomSheet(
        content=sheet_content,
        show_drag_handle=True,
        dismissible=True,
        enable_drag=True,
    )
    return sheet


def build_alert_conditions_screen(
    page: ft.Page,
    db,
    indicators: list,
    symbol: str | None = None,
    on_navigate=None,
) -> ft.Control:
    """Build the alert conditions configuration screen."""

    # -- Header --
    title_text = "Alert Conditions"
    if symbol:
        title_text = f"Alerts - {symbol}"

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
                    title_text,
                    size=22,
                    weight=ft.FontWeight.W_700,
                    color=ft.Colors.WHITE,
                ),
                ft.Container(width=48),  # spacer for centering
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.Padding(left=4, top=12, right=12, bottom=8),
    )

    # -- Load saved indicator states --
    all_settings = db.get_all_settings()

    def _is_enabled(ind_name: str) -> bool:
        val = all_settings.get(f"indicator_{ind_name}_enabled", "true")
        return val.lower() == "true"

    def _get_params(ind_name: str) -> dict:
        import json
        raw = all_settings.get(f"indicator_{ind_name}_params")
        if raw:
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                pass
        return {}

    # -- Global cooldown slider --
    cooldown_val = float(all_settings.get("cooldown_minutes", "5"))

    cooldown_slider = ft.Slider(
        min=1,
        max=15,
        value=cooldown_val,
        divisions=14,
        label="{value} min",
        active_color=ft.Colors.TEAL,
        inactive_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
    )

    def _on_cooldown_change(e):
        db.set_setting("cooldown_minutes", str(int(cooldown_slider.value)))

    cooldown_slider.on_change_end = _on_cooldown_change

    cooldown_section = _glass_card(
        ft.Column(
            [
                ft.Text(
                    "Global Cooldown",
                    size=15,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "Minimum time between repeated alerts for the same condition",
                    size=12,
                    color=ft.Colors.WHITE54,
                ),
                cooldown_slider,
            ],
            spacing=6,
        )
    )

    # -- Test Alert button --
    def _send_test(e):
        snackbar = ft.SnackBar(
            content=ft.Text("Test alert sent!", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.TEAL_700,
            duration=2000,
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()

    test_button = ft.Container(
        content=ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.NOTIFICATION_ADD_ROUNDED, color=ft.Colors.WHITE, size=20),
                    ft.Text("Test Alert", color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.TEAL),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=16),
                padding=ft.padding.Padding(left=32, top=14, right=32, bottom=14),
                side=ft.BorderSide(1, ft.Colors.with_opacity(0.3, ft.Colors.TEAL)),
            ),
            on_click=_send_test,
        ),
        alignment=ft.alignment.Alignment(0, 0),
        padding=ft.padding.Padding(left=0, top=8, right=0, bottom=8),
    )

    # -- Indicator cards --
    indicator_cards = []

    for ind in indicators:
        enabled = _is_enabled(ind.name)
        params = _get_params(ind.name)

        toggle = ft.Switch(
            value=enabled,
            active_color=ft.Colors.TEAL,
            active_track_color=ft.Colors.with_opacity(0.4, ft.Colors.TEAL),
        )

        param_badge = ft.Container(
            content=ft.Text(
                f"{len(ind.default_params)} params",
                size=11,
                color=ft.Colors.WHITE54,
            ),
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            border_radius=10,
            padding=ft.padding.Padding(left=10, top=3, right=10, bottom=3),
        )

        def _make_toggle_handler(ind_name, sw):
            def handler(e):
                db.set_setting(f"indicator_{ind_name}_enabled", "true" if sw.value else "false")
            return handler

        toggle.on_change = _make_toggle_handler(ind.name, toggle)

        def _open_params(ind_ref, current_p):
            def handler(e):
                import json

                def on_save(updated):
                    db.set_setting(
                        f"indicator_{ind_ref.name}_params",
                        json.dumps(updated),
                    )
                    page.update()

                sheet = _param_editor_sheet(page, ind_ref, current_p, on_save)
                page.open(sheet)

            return handler

        card_body = ft.GestureDetector(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                ind.name.replace("_", " ").title(),
                                size=16,
                                weight=ft.FontWeight.W_600,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                ind.description,
                                size=12,
                                color=ft.Colors.WHITE54,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                    param_badge,
                    toggle,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            on_tap=_open_params(ind, params) if ind.default_params else None,
        )

        indicator_cards.append(_glass_card(card_body, padding=ft.padding.Padding(left=20, top=14, right=20, bottom=14)))

    if not indicator_cards:
        indicator_cards.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=48, color=ft.Colors.WHITE24),
                        ft.Text("No indicators available", size=15, color=ft.Colors.WHITE54),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.alignment.Alignment(0, 0),
                padding=ft.padding.Padding(left=0, top=60, right=0, bottom=0),
            )
        )

    indicators_list = ft.Column(
        controls=[
            ft.Container(
                content=ft.Text(
                    "Indicators",
                    size=15,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE70,
                ),
                padding=ft.padding.Padding(left=4, top=8, right=0, bottom=4),
            ),
            *indicator_cards,
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # -- Assemble --
    body = ft.Column(
        [
            header,
            ft.Container(
                content=ft.Column(
                    [cooldown_section, test_button],
                    spacing=0,
                ),
                padding=ft.padding.Padding(left=16, top=0, right=16, bottom=0),
            ),
            ft.Container(
                content=indicators_list,
                expand=True,
                padding=ft.padding.Padding(left=16, top=0, right=16, bottom=0),
            ),
        ],
        spacing=4,
        expand=True,
    )

    return body
