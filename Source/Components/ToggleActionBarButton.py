from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from Components.ActionBarButton import action_bar_button_style


def ToggleActionBarButton(icon, tooltip, is_active, active_bg="#4CAF50", active_border="#4CAF50",
                          active_hover="#45a049", active_pressed="#3d8b40",
                          inactive_hover="#fffde7", inactive_border="#ffc107", inactive_pressed="#fff9c4"):
    """
    Create a toggle action bar button with two states (active/inactive)

    Args:
        icon: Emoji or text to display
        tooltip: Tooltip text
        is_active: Initial active state (True/False)
        active_bg: Background color when active (default: green)
        active_border: Border color when active (default: green)
        active_hover: Hover color when active (default: dark green)
        active_pressed: Pressed color when active (default: darker green)
        inactive_hover: Hover color when inactive (default: light yellow)
        inactive_border: Border color on hover when inactive (default: yellow)
        inactive_pressed: Pressed color when inactive (default: lighter yellow)

    Returns:
        tuple: (button, update_style_function)
            - button: QPushButton configured for action bar
            - update_style_function: Function to call with boolean to update style
    """
    button = QPushButton(icon)
    button.setFixedSize(32, 32)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setToolTip(tooltip)

    def update_style(is_active):
        if is_active:
            button.setStyleSheet(action_bar_button_style(active_bg, active_border, active_hover, active_hover, active_pressed))
        else:
            button.setStyleSheet(action_bar_button_style("white", "#e0e0e0", inactive_hover, inactive_border, inactive_pressed))

    # Set initial style
    update_style(is_active)

    return button, update_style
