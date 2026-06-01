"""Alert history screen for Alertra."""

import flet as ft
from datetime import datetime, timedelta


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


def _parse_timestamp(ts_str: str) -> datetime | None:
    """Try to parse the triggered_at timestamp."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(ts_str, fmt)
        except (ValueError, TypeError):
            continue
    return None


def _format_time(ts_str: str) -> str:
    dt = _parse_timestamp(ts_str)
    if dt is None:
        return ts_str or "--"
    now = datetime.now()
    diff = now - dt
    if diff < timedelta(minutes=1):
        return "Just now"
    if diff < timedelta(hours=1):
        mins = int(diff.total_seconds() / 60)
        return f"{mins}m ago"
    if diff < timedelta(days=1):
        hrs = int(diff.total_seconds() / 3600)
        return f"{hrs}h ago"
    return dt.strftime("%b %d, %H:%M")


def _is_within_24h(ts_str: str) -> bool:
    dt = _parse_timestamp(ts_str)
    if dt is None:
        return False
    return (datetime.now() - dt) < timedelta(hours=24)


def _alert_entry(alert: dict) -> ft.Container:
    """Build a single alert history entry as a glass card."""
    symbol = alert.get("symbol", "--")
    condition = alert.get("condition", "--")
    price = alert.get("price")
    message = alert.get("message", "")
    triggered_at = alert.get("triggered_at", "")
    is_read = alert.get("is_read", 0)

    price_str = f"${price:,.2f}" if price else "--"
    time_str = _format_time(triggered_at)

    # Indicator icon
    if "volume" in condition.lower():
        icon = ft.Icons.BAR_CHART_ROUNDED
    elif "camarilla" in condition.lower() or "pivot" in condition.lower():
        icon =ft.Icons.TRENDING_UP_ROUNDED
    else:
        icon =ft.Icons.NOTIFICATION_IMPORTANT_ROUNDED

    unread_dot = ft.Container(
        width=8,
        height=8,
        bgcolor=ft.Colors.TEAL,
        border_radius=4,
        visible=not is_read,
    )

    content = ft.Row(
        [
            ft.Container(
                content=ft.Icon(icon, color=ft.Colors.TEAL_200, size=22),
                bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.TEAL),
                border_radius=14,
                padding=8,
                width=44,
                height=44,
                alignment=ft.alignment.center,
            ),
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                symbol,
                                size=16,
                                weight=ft.FontWeight.W_700,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                condition.replace("_", " ").title(),
                                size=12,
                                color=ft.Colors.TEAL_200,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        message or f"Price: {price_str}",
                        size=12,
                        color=ft.Colors.WHITE54,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=3,
                expand=True,
            ),
            ft.Column(
                [
                    unread_dot,
                    ft.Text(
                        time_str,
                        size=11,
                        color=ft.Colors.WHITE38,
                    ),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.END,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
    )

    return _glass_card(content, padding=ft.padding.symmetric(horizontal=16, vertical=12))


def _empty_state(tab_name: str) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(
                    ft.Icons.NOTIFICATIONS_NONE_ROUNDED,
                    size=64,
                    color=ft.Colors.WHITE24,
                ),
                ft.Text(
                    "No alerts yet",
                    size=18,
                    color=ft.Colors.WHITE54,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Text(
                    "Alerts will appear here when conditions are triggered",
                    size=13,
                    color=ft.Colors.WHITE38,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        alignment=ft.alignment.center,
        expand=True,
        padding=ft.padding.only(top=60),
    )


def build_history_screen(
    page: ft.Page,
    db,
    on_navigate=None,
) -> ft.Control:
    """Build the alert history screen with Active/All tabs."""

    active_list = ft.ListView(expand=True, spacing=0, auto_scroll=False)
    all_list = ft.ListView(expand=True, spacing=0, auto_scroll=False)

    def _load_alerts():
        alerts = db.get_alerts(limit=200)

        active_alerts = [a for a in alerts if _is_within_24h(a.get("triggered_at", ""))]

        active_list.controls.clear()
        if active_alerts:
            for alert in active_alerts:
                active_list.controls.append(_alert_entry(alert))
        else:
            active_list.controls.append(_empty_state("Active"))

        all_list.controls.clear()
        if alerts:
            for alert in alerts:
                all_list.controls.append(_alert_entry(alert))
        else:
            all_list.controls.append(_empty_state("All"))

        page.update()

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
                    "Alert History",
                    size=22,
                    weight=ft.FontWeight.W_700,
                    color=ft.Colors.WHITE,
                ),
                ft.Container(width=48),  # spacer
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(left=4, right=12, top=12, bottom=4),
    )

    # -- Tabs --
    tab_bar = ft.Container(
        content=ft.Row(
            [
                tab_btn := ft.Container(
                    content=ft.Text(
                        "Active",
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.WHITE,
                    ),
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.TEAL),
                    border_radius=14,
                    padding=ft.padding.symmetric(horizontal=24, vertical=10),
                    animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
                ),
                tab_btn_all := ft.Container(
                    content=ft.Text(
                        "All",
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.WHITE54,
                    ),
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                    border_radius=14,
                    padding=ft.padding.symmetric(horizontal=24, vertical=10),
                    animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
                ),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
    )

    content_stack = ft.Stack(
        [
            ft.Container(content=active_list, expand=True, visible=True),
            ft.Container(content=all_list, expand=True, visible=False),
        ],
        expand=True,
    )

    def _switch_tab(e, idx):
        tab_index.current = idx
        content_stack.controls[0].visible = (idx == 0)
        content_stack.controls[1].visible = (idx == 1)

        if idx == 0:
            tab_btn.bgcolor = ft.Colors.with_opacity(0.2, ft.Colors.TEAL)
            tab_btn.content.color = ft.Colors.WHITE
            tab_btn.content.weight = ft.FontWeight.W_600
            tab_btn_all.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
            tab_btn_all.content.color = ft.Colors.WHITE54
            tab_btn_all.content.weight = ft.FontWeight.W_500
        else:
            tab_btn.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
            tab_btn.content.color = ft.Colors.WHITE54
            tab_btn.content.weight = ft.FontWeight.W_500
            tab_btn_all.bgcolor = ft.Colors.with_opacity(0.2, ft.Colors.TEAL)
            tab_btn_all.content.color = ft.Colors.WHITE
            tab_btn_all.content.weight = ft.FontWeight.W_600

        page.update()

    tab_btn.on_click = lambda e: _switch_tab(e, 0)
    tab_btn_all.on_click = lambda e: _switch_tab(e, 1)

    # -- Clear All button --
    def _confirm_clear(e):
        def _do_clear(e2):
            db.clear_alerts()
            _load_alerts()
            page.close(confirm_dialog)

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Clear All Alerts", color=ft.Colors.WHITE),
            content=ft.Text(
                "This will permanently delete all alert history. Continue?",
                color=ft.Colors.WHITE70,
            ),
            bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.GREY_900),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e2: page.close(confirm_dialog)),
                ft.ElevatedButton(
                    "Clear All",
                    bgcolor=ft.Colors.RED_700,
                    color=ft.Colors.WHITE,
                    on_click=_do_clear,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(confirm_dialog)

    clear_btn = ft.Container(
        content=ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.DELETE_SWEEP_ROUNDED, color=ft.Colors.RED_300, size=18),
                    ft.Text("Clear All", color=ft.Colors.RED_300, weight=ft.FontWeight.W_500),
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.RED),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                side=ft.BorderSide(1, ft.Colors.with_opacity(0.2, ft.Colors.RED)),
            ),
            on_click=_confirm_clear,
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.only(bottom=8, top=4),
    )

    # -- Assemble --
    body = ft.Column(
        [
            header,
            tab_bar,
            clear_btn,
            ft.Container(
                content=content_stack,
                expand=True,
                padding=ft.padding.symmetric(horizontal=16),
            ),
        ],
        spacing=0,
        expand=True,
    )

    _load_alerts()

    return body
