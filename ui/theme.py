"""
Theme configuration for Alertra's liquid glass UI.
"""

import flet as ft


# Accent colors
ACCENT_COLORS = {
    "teal": ft.Colors.TEAL,
    "blue": ft.Colors.BLUE,
    "purple": ft.Colors.PURPLE,
    "orange": ft.Colors.ORANGE,
}

# Default accent
DEFAULT_ACCENT = "teal"


def get_accent_color(name: str = DEFAULT_ACCENT) -> str:
    return ACCENT_COLORS.get(name, ACCENT_COLORS[DEFAULT_ACCENT])


def get_theme(accent: str = DEFAULT_ACCENT, mode: str = "dark") -> ft.Theme:
    """Create Flet theme with liquid glass styling."""
    accent_color = get_accent_color(accent)

    if mode == "dark":
        return ft.Theme(
            color_scheme_seed=accent_color,
            color_scheme=ft.ColorScheme(
                primary=accent_color,
                surface=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                surface_variant=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
                background=ft.Colors.GREY_900,
                on_background=ft.Colors.WHITE,
                on_surface=ft.Colors.WHITE,
                on_surface_variant=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
            ),
            text_theme=ft.TextTheme(
                body_medium=ft.TextStyle(color=ft.Colors.WHITE),
                body_small=ft.TextStyle(color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                title_large=ft.TextStyle(color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                title_medium=ft.TextStyle(color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                label_large=ft.TextStyle(color=ft.Colors.WHITE),
            ),
        )
    else:
        return ft.Theme(
            color_scheme_seed=accent_color,
            color_scheme=ft.ColorScheme(
                primary=accent_color,
                surface=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                surface_variant=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                background=ft.Colors.GREY_100,
                on_background=ft.Colors.BLACK,
                on_surface=ft.Colors.BLACK,
                on_surface_variant=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
            ),
        )


def glass_container(
    content: ft.Control,
    padding: float = 16,
    margin_bottom: float = 8,
    border_radius: float = 24,
    expand: bool = False,
) -> ft.Container:
    """Create a glass-morphism container."""
    return ft.Container(
        content=content,
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
        border_radius=border_radius,
        border=ft.border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
        blur=ft.Blur(10, 10, ft.BlurMode.NORMAL),
        padding=padding,
        margin=ft.margin.only(bottom=margin_bottom),
        expand=expand,
    )


def glass_card(
    content: ft.Control,
    padding: float = 16,
    border_radius: float = 24,
    on_tap=None,
) -> ft.Container:
    """Create a clickable glass card."""
    return ft.Container(
        content=content,
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
        border_radius=border_radius,
        border=ft.border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
        blur=ft.Blur(8, 8, ft.BlurMode.NORMAL),
        padding=padding,
        margin=ft.margin.only(bottom=8),
        on_click=on_tap,
        animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )


def glass_appbar(title: str, actions: list = None) -> ft.AppBar:
    """Create a glass-styled app bar."""
    return ft.AppBar(
        title=ft.Text(title, weight=ft.FontWeight.BOLD, size=20),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        elevation=0,
        actions=actions or [],
    )
