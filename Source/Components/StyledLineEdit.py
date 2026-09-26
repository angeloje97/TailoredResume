from PySide6.QtWidgets import QLineEdit


def StyledLineEdit(placeholder="", text="", font_size=11, margin_y=0, on_change=None):
    """
    Create a rounded single-line input with a green focus border

    Args:
        placeholder: Placeholder text (default: "")
        text: Initial text (default: "")
        font_size: Font size in pt (default: 11)
        margin_y: Top and bottom margin in px (default: 0)
        on_change: Callback connected to textChanged (default: None)

    Returns:
        QLineEdit
    """
    line_edit = QLineEdit()
    line_edit.setPlaceholderText(placeholder)
    line_edit.setText(text)
    line_edit.setMinimumHeight(40)
    line_edit.setStyleSheet(f"""
        QLineEdit {{
            padding: 10px;
            font-size: {font_size}pt;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background-color: white;
            margin-top: {margin_y}px;
            margin-bottom: {margin_y}px;
        }}
        QLineEdit:focus {{
            border: 2px solid #4CAF50;
        }}
    """)

    if on_change:
        line_edit.textChanged.connect(on_change)

    return line_edit
