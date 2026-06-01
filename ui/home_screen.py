"""Main watchlist dashboard screen for Alertra."""

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


def _format_volume(vol: float) -> str:
    if vol >= 1_000_000_000:
        return f"{vol / 1_000_000_000:.1f}B"
    if vol >= 1_000_000:
        return f"{vol / 1_000_000:.1f}M"
    if vol >= 1_000:
        return f"{vol / 1_000:.1f}K"
    return f"{vol:,.0f}"


def _symbol_card(
    item: dict,
    quote: dict | None,
    on_delete,
    on_edit_alerts,
) -> ft.Dismissible:
    """Build a swipeable symbol card."""
    symbol = item["symbol"]
    display = item.get("display_name") or symbol

    if quote:
        price = quote.get("price", 0.0)
        change_pct = quote.get("change_pct", 0.0)
        volume = quote.get("volume", 0.0)
        price_str = f"${price:,.2f}"
        is_up = change_pct >= 0
        change_color = ft.Colors.GREEN_400 if is_up else ft.Colors.RED_400
        change_str = f"{'+' if is_up else ''}{change_pct:.2f}%"
        vol_str = _format_volume(volume)
    else:
        price_str = "--"
        change_str = "--"
        vol_str = "--"
        change_color = ft.Colors.WHITE54

    card_content = ft.Row(
        [
            ft.Column(
                [
                    ft.Text(
                        symbol,
                        size=22,
                        weight=ft.FontWeight.W_700,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Text(
                        display,
                        size=12,
                        color=ft.Colors.WHITE54,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=2,
                expand=True,
            ),
            ft.Column(
                [
                    ft.Text(
                        price_str,
                        size=18,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.RIGHT,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                change_str,
                                size=13,
                                weight=ft.FontWeight.W_500,
                                color=change_color,
                            ),
                            ft.Text(
                                vol_str,
                                size=12,
                                color=ft.Colors.WHITE54,
                            ),
                        ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.END,
            ),
            ft.Icon(
                ft.Icons.NOTIFICATIONS_ACTIVE_ROUNDED,
                color=ft.Colors.with_opacity(0.6, ft.Colors.TEAL),
                size=20,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    card = _glass_card(card_content, padding=ft.padding.symmetric(horizontal=20, vertical=14))

    return ft.Dismissible(
        content=card,
        dismiss_direction=ft.DismissDirection.HORIZONTAL,
        background=ft.Container(
            bgcolor=ft.Colors.RED_700,
            border_radius=24,
            alignment=ft.alignment.center_left,
            padding=ft.padding.only(left=30),
            content=ft.Icon(ft.Icons.DELETE_OUTLINE, color=ft.Colors.WHITE, size=28),
        ),
        secondary_background=ft.Container(
            bgcolor=ft.Colors.TEAL_700,
            border_radius=24,
            alignment=ft.alignment.center_right,
            padding=ft.padding.only(right=30),
            content=ft.Icon(ft.Icons.TUNE_ROUNDED, color=ft.Colors.WHITE, size=28),
        ),
        dismiss_thresholds={
            ft.DismissDirection.START_TO_END: 0.4,
            ft.DismissDirection.END_TO_START: 0.4,
        },
        on_dismiss=lambda e: _handle_dismiss(e, item, on_delete, on_edit_alerts),
    )


def _handle_dismiss(e, item, on_delete, on_edit_alerts):
    direction = e.control.dismiss_direction
    if direction == ft.DismissDirection.START_TO_END:
        on_delete(item)
    else:
        on_edit_alerts(item)


def _empty_state() -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(
                    ft.Icons.SEARCH_OFF_ROUNDED,
                    size=64,
                    color=ft.Colors.WHITE24,
                ),
                ft.Text(
                    "No symbols yet",
                    size=18,
                    color=ft.Colors.WHITE54,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Text(
                    "Tap + to add a stock to your watchlist",
                    size=13,
                    color=ft.Colors.WHITE38,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        alignment=ft.alignment.center,
        expand=True,
        padding=ft.padding.only(top=80),
    )


def build_home_screen(
    page: ft.Page,
    db,
    provider,
    on_navigate=None,
) -> ft.Control:
    """Build the main watchlist dashboard screen."""

    # State
    quotes: dict[str, dict] = {}
    current_watchlist_id = None

    # -- App bar --
    unread_count = len(db.get_alerts(limit=999, unread_only=True))

    alert_badge = ft.Badge(
        content=ft.Icon(ft.Icons.NOTIFICATIONS_NONE_ROUNDED, color=ft.Colors.WHITE, size=26),
        value=str(unread_count) if unread_count > 0 else None,
        bgcolor=ft.Colors.TEAL,
        text_color=ft.Colors.WHITE,
        visible=unread_count > 0,
    )

    def open_history(e):
        if on_navigate:
            on_navigate("history")

    def open_settings(e):
        if on_navigate:
            on_navigate("settings")

    app_bar = ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    "Alertra",
                    size=28,
                    weight=ft.FontWeight.W_800,
                    color=ft.Colors.WHITE,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.center_left,
                        end=ft.alignment.center_right,
                        colors=[ft.Colors.TEAL_200, ft.Colors.TEAL],
                    ),
                ),
                ft.Row(
                    [
                        ft.GestureDetector(
                            content=alert_badge,
                            on_tap=open_history,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.SETTINGS_OUTLINED,
                            icon_color=ft.Colors.WHITE70,
                            icon_size=26,
                            on_click=open_settings,
                        ),
                    ],
                    spacing=4,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(left=20, right=12, top=12, bottom=8),
    )

    # -- Watchlist selector --
    watchlists = db.get_watchlists()

    if not watchlists:
        db.create_watchlist("Default")
        watchlists = db.get_watchlists()

    active_wl = db.get_active_watchlist()
    if active_wl:
        current_watchlist_id = active_wl["id"]
    else:
        current_watchlist_id = watchlists[0]["id"]
        db.set_active_watchlist(current_watchlist_id)

    wl_dropdown = ft.Dropdown(
        value=str(current_watchlist_id),
        options=[
            ft.dropdown.Option(str(wl["id"]), wl["name"]) for wl in watchlists
        ],
        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        border_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
        border_radius=16,
        text_style=ft.TextStyle(color=ft.Colors.WHITE, size=14),
        content_padding=ft.padding.symmetric(horizontal=16, vertical=10),
        width=220,
        dense=True,
    )

    symbols_list = ft.ListView(expand=True, spacing=0, auto_scroll=False)

    def load_symbols():
        symbols_list.controls.clear()
        items = db.get_symbols(current_watchlist_id)

        if not items:
            symbols_list.controls.append(_empty_state())
            page.update()
            return

        for item in items:
            q = quotes.get(item["symbol"])
            card = _symbol_card(
                item,
                q,
                on_delete=_delete_symbol,
                on_edit_alerts=_edit_alerts,
            )
            symbols_list.controls.append(card)

        page.update()

    def _delete_symbol(item):
        db.remove_symbol(item["id"])
        load_symbols()

    def _edit_alerts(item):
        if on_navigate:
            on_navigate("alerts", symbol=item["symbol"])

    def _on_watchlist_change(e):
        nonlocal current_watchlist_id
        current_watchlist_id = int(wl_dropdown.value)
        db.set_active_watchlist(current_watchlist_id)
        load_symbols()

    wl_dropdown.on_change = _on_watchlist_change

    # -- Pull-to-refresh wrapper --
    async def _refresh_quotes(e=None):
        items = db.get_symbols(current_watchlist_id)
        for item in items:
            sym = item["symbol"]
            try:
                q = await provider.get_quote(sym)
                if q:
                    quotes[sym] = q
            except Exception:
                pass
        load_symbols()

    refresh_btn = ft.IconButton(
        icon=ft.Icons.REFRESH_ROUNDED,
        icon_color=ft.Colors.WHITE60,
        icon_size=22,
        on_click=_refresh_quotes,
    )

    selector_row = ft.Container(
        content=ft.Row(
            [wl_dropdown, refresh_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=4),
    )

    # -- FAB (add symbol) --
    def open_search(e):
        if on_navigate:
            on_navigate("search")

    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD_ROUNDED,
        bgcolor=ft.Colors.TEAL,
        foreground_color=ft.Colors.WHITE,
        shape=ft.CircleBorder(),
        elevation=6,
        on_click=open_search,
    )

    # -- Assemble screen --
    body = ft.Column(
        [
            app_bar,
            selector_row,
            ft.Container(
                content=symbols_list,
                expand=True,
                padding=ft.padding.symmetric(horizontal=16),
            ),
        ],
        spacing=4,
        expand=True,
    )

    scaffold = ft.Stack(
        [body],
        alignment=ft.alignment.bottom_right,
        expand=True,
    )

    # Overlay the FAB
    scaffold.controls.append(
        ft.Container(
            content=fab,
            right=20,
            bottom=24,
            alignment=ft.alignment.center_right,
        )
    )

    # Load initial data
    load_symbols()

    # Kick off an initial quote fetch (non-blocking)
    page.run_task(_refresh_quotes)

    return scaffold
