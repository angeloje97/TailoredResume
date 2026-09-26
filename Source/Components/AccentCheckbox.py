from PySide6.QtWidgets import QCheckBox


def AccentCheckbox(label, hover_border, hover_background, background="white", border="#e0e0e0",
                   font_size=12, padding=10, margin_y=0, tooltip="", on_change=None):
    """
    Create a boxed checkbox with a colored hover state (filter toggles, Save Submission)

    Args:
        label: Checkbox text
        hover_border: Border color on hover
        hover_background: Background color on hover
        background: Background color (default: white)
        border: Border color (default: light gray)
        font_size: Font size in pt (default: 12)
        padding: Padding in px (default: 10)
        margin_y: Top and bottom margin in px (default: 0)
        tooltip: Tooltip text (default: "")
        on_change: Callback connected to stateChanged (default: None)

    Returns:
        QCheckBox
    """
    checkbox = QCheckBox(label)
    checkbox.setMinimumHeight(40)
    checkbox.setStyleSheet(f"""
        QCheckBox {{
            font-size: {font_size}pt;
            color: #333;
            padding: {padding}px;
            background-color: {background};
            border: 2px solid {border};
            border-radius: 8px;
            margin-top: {margin_y}px;
            margin-bottom: {margin_y}px;
            padding-left: 12px;
        }}
        QCheckBox:hover {{
            border: 2px solid {hover_border};
            background-color: {hover_background};
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
        }}
    """)

    if tooltip:
        checkbox.setToolTip(tooltip)

    if on_change:
        checkbox.stateChanged.connect(on_change)

    return checkbox
