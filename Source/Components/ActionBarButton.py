from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt


def action_bar_button_style(background, border, hover_color, hover_border, pressed_color):
    """Stylesheet shared by ActionBarButton and ToggleActionBarButton"""
    return f"""
        QPushButton {{
            background-color: {background};
            border: 1px solid {border};
            border-radius: 6px;
            font-size: 14pt;
            padding: 0px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
            border: 1px solid {hover_border};
        }}
        QPushButton:pressed {{
            background-color: {pressed_color};
        }}
    """


def ActionBarButton(icon, tooltip, on_click, hover_color="#e3f2fd", hover_border="#2196F3", pressed_color="#bbdefb"):
    """
    Create a consistent action bar button with icon

    Args:
        icon: Emoji or text to display
        tooltip: Tooltip text
        on_click: Callback function that takes an event parameter
        hover_color: Background color on hover (default: light blue)
        hover_border: Border color on hover (default: blue)
        pressed_color: Background color when pressed (default: darker blue)

    Returns:
        QPushButton configured for action bar
    """
    button = QPushButton(icon)
    button.setFixedSize(32, 32)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setToolTip(tooltip)
    button.setStyleSheet(action_bar_button_style("white", "#e0e0e0", hover_color, hover_border, pressed_color))
    button.mousePressEvent = on_click

    return button
