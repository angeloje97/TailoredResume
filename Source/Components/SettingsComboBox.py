from PySide6.QtWidgets import QVBoxLayout, QLabel
from Components.StyledComboBox import StyledComboBox


def SettingsComboBox(label, layout_obj, items, current=None, on_change=None):
    """
    Create a labeled dropdown for the settings page

    Args:
        label: Text shown above the dropdown
        layout_obj: Parent layout to add the label + dropdown to
        items: List of option strings
        current: Initially selected text (default: None, first item)
        on_change: Callback connected to currentTextChanged (default: None)

    Returns:
        QComboBox
    """
    combo_layout = QVBoxLayout()
    combo_layout.setSpacing(8)

    title_label = QLabel(label)
    title_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #333;")
    combo_layout.addWidget(title_label)

    combo = StyledComboBox(items, current, on_change)
    combo_layout.addWidget(combo)

    layout_obj.addLayout(combo_layout)

    return combo
