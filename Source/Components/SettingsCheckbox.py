from PySide6.QtWidgets import QHBoxLayout, QCheckBox


def SettingsCheckbox(label, layout_obj, is_checked=False, on_change=None, tooltip="", indent=0):
    """
    Create a reusable settings checkbox with consistent styling

    Args:
        label: Text label for the checkbox
        layout_obj: Parent layout to add the checkbox to
        is_checked: Initial checked state (default: False)
        on_change: Callback function when state changes (default: None)
        tooltip: Tooltip text (default: "")
        indent: Left padding in pixels for visual hierarchy (default: 0)

    Returns:
        QCheckBox configured for settings page
    """
    checkbox_layout = QHBoxLayout()
    checkbox_layout.setSpacing(10)

    checkbox = QCheckBox(label)
    checkbox.setChecked(is_checked)
    checkbox.setStyleSheet(f"""
        QCheckBox {{
            font-size: 12pt;
            color: #333;
            padding: 8px;
            padding-left: {12 + indent}px;
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

    checkbox_layout.addWidget(checkbox)
    checkbox_layout.addStretch()
    layout_obj.addLayout(checkbox_layout)

    return checkbox
