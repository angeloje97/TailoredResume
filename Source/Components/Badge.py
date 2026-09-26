from PySide6.QtWidgets import QLabel


def Badge(text, color="#757575", background="#f5f5f5", font_size=9, weight=None, border=None, tooltip=""):
    """
    Create a small rounded pill label (salary, date range, status, etc.)

    Args:
        text: Text to display
        color: Text color (default: gray)
        background: Background color (default: light gray)
        font_size: Font size in pt (default: 9)
        weight: CSS font-weight, e.g. "600" or "bold" (default: None, normal weight)
        border: Border color for a 2px outline (default: None, no border)
        tooltip: Tooltip text (default: "")

    Returns:
        QLabel styled as a badge
    """
    badge = QLabel(text)
    badge.setStyleSheet(f"""
        font-size: {font_size}pt;
        color: {color};
        background-color: {background};
        padding: 4px 10px;
        border-radius: 6px;
        {f"font-weight: {weight};" if weight else ""}
        {f"border: 2px solid {border};" if border else ""}
    """)

    if tooltip:
        badge.setToolTip(tooltip)

    return badge
