from PySide6.QtWidgets import QLabel


def PageTitle(text):
    """Create the large bold heading shown at the top of each page"""
    title_label = QLabel(text)
    title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
    return title_label
