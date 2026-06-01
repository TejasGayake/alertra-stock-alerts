"""Search overlay/modal for adding symbols to watchlist."""

import flet as ft
from ui.theme import border_all


def _glass_card(content: ft.Control, **kwargs) -> ft.Container:
    """Wrap content in a liquid-glass styled container."""
    defaults = dict(
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        border_radius=24,
        border=border_all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
        blur=ft.Blur(10, 10),
        padding=16,
        margin=ft.margin.Margin(left=0, top=0, right=0, bottom=8),
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )
    defaults.update(kwargs)
    return ft.Container(content=content, **defaults)


def build_search_overlay(
    page: ft.Page,
    provider,
    db,
    on_add_symbol=None,
) -> ft.Control:
    """Build a search modal overlay for adding symbols."""

    recent_searches: list[str] = []
    saved_recent = db.get_setting("recent_searches", "")
    if saved_recent:
        recent_searches = [s.strip() for s in saved_recent.split(",") if s.strip()]

    results_list = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
    recent_section = ft.Column(spacing=0)

    search_input = ft.TextField(
        hint_text="Search symbol or company name...",
        hint_style=ft.TextStyle(color=ft.Colors.WHITE38, size=15),
        text_style=ft.TextStyle(color=ft.Colors.WHITE, size=15),
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        border_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
        border_radius=16,
        content_padding=ft.padding.Padding(left=20, top=14, right=20, bottom=14),
        cursor_color=ft.Colors.TEAL,
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        autofocus=True,
        dense=True,
    )

    loading_indicator = ft.Container(
        content=ft.ProgressRing(
            color=ft.Colors.TEAL,
            stroke_width=2.5,
            width=20,
            height=20,
        ),
        alignment=ft.alignment.Alignment(0, 0),
        padding=ft.padding.Padding(left=0, top=16, right=0, bottom=16),
        visible=False,
    )

    def _save_recent():
        db.set_setting("recent_searches", ",".join(recent_searches[:10]))

    def _add_to_recent(symbol: str):
        if symbol in recent_searches:
            recent_searches.remove(symbol)
        recent_searches.insert(0, symbol)
        if len(recent_searches) > 10:
            recent_searches.pop()
        _save_recent()

    def _add_symbol(symbol: str, name: str | None = None):
        # Find active watchlist
        active_wl = db.get_active_watchlist()
        if not active_wl:
            watchlists = db.get_watchlists()
            if watchlists:
                active_wl = watchlists[0]
                db.set_active_watchlist(active_wl["id"])
            else:
                wl_id = db.create_watchlist("Default")
                active_wl = {"id": wl_id}

        # Check if symbol already exists
        existing = db.get_symbols(active_wl["id"])
        if any(item["symbol"] == symbol for item in existing):
            snack = ft.SnackBar(
                content=ft.Text(f"{symbol} is already in your watchlist", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.GREY_800),
                duration=2000,
            )
            page.open(snack)
            return

        db.add_symbol(active_wl["id"], symbol, name)
        _add_to_recent(symbol)

        snack = ft.SnackBar(
            content=ft.Text(f"{symbol} added to watchlist", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.TEAL_700,
            duration=1500,
        )
        page.open(snack)

        if on_add_symbol:
            on_add_symbol(symbol, name)

    def _make_result_card(symbol: str, name: str, exchange: str) -> ft.GestureDetector:
        def on_tap(e):
            _add_symbol(symbol, name)

        return ft.GestureDetector(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(
                                symbol,
                                size=15,
                                weight=ft.FontWeight.W_700,
                                color=ft.Colors.WHITE,
                            ),
                            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.TEAL),
                            border_radius=10,
                            padding=ft.padding.Padding(left=12, top=6, right=12, bottom=6),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    name,
                                    size=13,
                                    color=ft.Colors.WHITE,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    exchange,
                                    size=11,
                                    color=ft.Colors.WHITE38,
                                ),
                            ],
                            spacing=1,
                            expand=True,
                        ),
                        ft.Icon(
                            ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                            color=ft.Colors.TEAL,
                            size=26,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.Padding(left=8, top=10, right=8, bottom=10),
                border_radius=16,
                bgcolor=ft.Colors.with_opacity(0.0, ft.Colors.WHITE),
                animate_bgcolor=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
            ),
            on_tap=on_tap,
        )

    async def _on_search_change(e):
        query = search_input.value.strip()

        if len(query) < 1:
            results_list.controls.clear()
            _render_recent()
            page.update()
            return

        # Show loading
        loading_indicator.visible = True
        recent_section.visible = False
        results_list.controls.clear()
        page.update()

        try:
            results = await provider.search_symbols(query)
        except Exception:
            results = []

        loading_indicator.visible = False
        results_list.controls.clear()

        if results:
            for r in results[:15]:
                results_list.controls.append(
                    _make_result_card(
                        r.get("symbol", ""),
                        r.get("name", ""),
                        r.get("exchange", ""),
                    )
                )
        else:
            results_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=40, color=ft.Colors.WHITE24),
                            ft.Text(
                                f'No results for "{query}"',
                                size=14,
                                color=ft.Colors.WHITE54,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    alignment=ft.alignment.Alignment(0, 0),
                    padding=ft.padding.Padding(left=0, top=32, right=0, bottom=32),
                )
            )

        page.update()

    search_input.on_change = _on_search_change

    def _render_recent():
        recent_section.controls.clear()
        if not recent_searches:
            recent_section.visible = False
            return

        recent_section.visible = True
        recent_section.controls.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text(
                            "Recent Searches",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.WHITE54,
                        ),
                        ft.GestureDetector(
                            content=ft.Text(
                                "Clear",
                                size=12,
                                color=ft.Colors.TEAL_200,
                                weight=ft.FontWeight.W_500,
                            ),
                            on_tap=lambda e: _clear_recent(),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.Padding(left=4, top=8, right=0, bottom=8),
            )
        )

        chip_row = ft.Wrap(
            spacing=8,
            run_spacing=8,
        )

        for sym in recent_searches:
            chip = ft.GestureDetector(
                content=ft.Container(
                    content=ft.Text(
                        sym,
                        size=13,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.W_500,
                    ),
                    bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
                    border=border_all(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
                    border_radius=14,
                    padding=ft.padding.Padding(left=16, top=8, right=16, bottom=8),
                ),
                on_tap=lambda e, s=sym: _quick_add(s),
            )
            chip_row.controls.append(chip)

        recent_section.controls.append(chip_row)

    def _quick_add(symbol: str):
        _add_symbol(symbol)
        _render_recent()
        page.update()

    def _clear_recent():
        recent_searches.clear()
        db.set_setting("recent_searches", "")
        _render_recent()
        page.update()

    def _close(e):
        page.close(overlay)

    _render_recent()

    # -- Build overlay content --
    overlay_content = ft.Container(
        content=ft.Column(
            [
                # Drag handle
                ft.Container(
                    width=40,
                    height=4,
                    bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
                    border_radius=2,
                    alignment=ft.alignment.Alignment(0, 0),
                    margin=ft.margin.Margin(left=0, top=0, right=0, bottom=12),
                ),
                # Header
                ft.Row(
                    [
                        ft.Text(
                            "Add Symbol",
                            size=22,
                            weight=ft.FontWeight.W_700,
                            color=ft.Colors.WHITE,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_ROUNDED,
                            icon_color=ft.Colors.WHITE54,
                            icon_size=26,
                            on_click=_close,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # Search field
                search_input,
                # Loading
                loading_indicator,
                # Results
                ft.Container(
                    content=results_list,
                    expand=True,
                    padding=ft.padding.Padding(left=0, top=4, right=0, bottom=0),
                ),
                # Recent
                recent_section,
            ],
            spacing=4,
            expand=True,
        ),
        bgcolor=ft.Colors.with_opacity(0.97, ft.Colors.GREY_900),
        border_radius=ft.border_radius.BorderRadius(top_left=24, top_right=24, bottom_left=0, bottom_right=0),
        border=ft.border.Border(
            top=ft.BorderSide(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
            bottom=ft.BorderSide(0, ft.Colors.TRANSPARENT),
            left=ft.BorderSide(0, ft.Colors.TRANSPARENT),
            right=ft.BorderSide(0, ft.Colors.TRANSPARENT),
        ),
        padding=ft.padding.Padding(left=20, top=8, right=20, bottom=16),
        height=page.height * 0.85 if page.height else 600,
        animate_position=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
    )

    overlay = ft.BottomSheet(
        content=overlay_content,
        show_drag_handle=False,
        dismissible=True,
    )

    return overlay
