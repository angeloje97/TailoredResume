from PySide6.QtWidgets import QPushButton

# variant: (background, text color, border, hover)
VARIANTS = {
    "blue":  ("#e3f2fd", "#1976d2", "#2196F3", "#bbdefb"),
    "green": ("#e8f5e9", "#2e7d32", "#4CAF50", "#c8e6c9"),
}


def ChipButton(text, on_click=None, variant="blue"):
    """
    Create a small tinted quick-select button (e.g. "Today", "+7 Days")

    Args:
        text: Button label
        on_click: Callback connected to clicked (default: None)
        variant: "blue" or "green" (default: "blue")

    Returns:
        QPushButton
    """
    background, color, border, hover = VARIANTS[variant]

    button = QPushButton(text)
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {background};
            color: {color};
            font-size: 10pt;
            font-weight: bold;
            border: 1px solid {border};
            border-radius: 6px;
            padding: 8px 12px;
        }}
        QPushButton:hover {{
            background-color: {hover};
        }}
    """)

    if on_click:
        button.clicked.connect(on_click)

    return button
