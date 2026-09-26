from PySide6.QtWidgets import QComboBox


def StyledComboBox(items, current=None, on_change=None, font_size=11, margin_y=0, min_width=None):
    """
    Create a rounded dropdown with a custom arrow

    Args:
        items: List of option strings
        current: Initially selected text (default: None, first item)
        on_change: Callback connected to currentTextChanged (default: None)
        font_size: Font size in pt (default: 11)
        margin_y: Top and bottom margin in px (default: 0)
        min_width: Minimum width in px (default: None)

    Returns:
        QComboBox
    """
    combo = QComboBox()
    combo.addItems(items)
    if current is not None:
        combo.setCurrentText(current)
    combo.setMinimumHeight(40)
    if min_width:
        combo.setMinimumWidth(min_width)
    combo.setStyleSheet(f"""
        QComboBox {{
            padding: 10px;
            font-size: {font_size}pt;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background-color: white;
            margin-top: {margin_y}px;
            margin-bottom: {margin_y}px;
        }}
        QComboBox:focus {{
            border: 2px solid #4CAF50;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #666;
            margin-right: 10px;
        }}
    """)

    if on_change:
        combo.currentTextChanged.connect(on_change)

    return combo
