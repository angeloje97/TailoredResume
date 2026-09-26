from PySide6.QtWidgets import QPushButton

# variant: (background, text color, border, hover, pressed)
VARIANTS = {
    "primary":   ("#4CAF50", "white", "none", "#45a049", "#3d8b40"),
    "secondary": ("#f5f5f5", "#333", "1px solid #e0e0e0", "#e0e0e0", None),
    "dark":      ("#2c3e50", "white", "none", "#34495e", "#1b2733"),
}

# size: (min height, font size in pt, border radius, padding)
SIZES = {
    "medium": (40, 11, 6, "8px 16px"),
    "large":  (50, 14, 5, "10px"),
}


def Button(text, on_click=None, variant="primary", size="medium"):
    """
    Create a solid text button (dialog actions, page submit buttons)

    Args:
        text: Button label
        on_click: Callback connected to clicked (default: None)
        variant: "primary" (green), "secondary" (gray), or "dark" (navy) (default: "primary")
        size: "medium" (dialog buttons) or "large" (page submit buttons) (default: "medium")

    Returns:
        QPushButton
    """
    background, color, border, hover, pressed = VARIANTS[variant]
    height, font_size, radius, padding = SIZES[size]

    button = QPushButton(text)
    button.setMinimumHeight(height)
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {background};
            color: {color};
            font-size: {font_size}pt;
            font-weight: bold;
            border: {border};
            border-radius: {radius}px;
            padding: {padding};
        }}
        QPushButton:hover {{
            background-color: {hover};
        }}
        {f"QPushButton:pressed {{ background-color: {pressed}; }}" if pressed else ""}
    """)

    if on_click:
        button.clicked.connect(on_click)

    return button
