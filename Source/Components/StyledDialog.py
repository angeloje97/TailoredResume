from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel


class StyledDialog(QDialog):
    """White dialog with a vertical layout (`self.body`) and an optional bold heading."""

    def __init__(self, parent, window_title, heading=None, min_width=None, min_size=None, margin=20, spacing=15):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        if min_width:
            self.setMinimumWidth(min_width)
        if min_size:
            self.setMinimumSize(*min_size)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)

        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(margin, margin, margin, margin)
        if spacing is not None:
            self.body.setSpacing(spacing)

        if heading:
            heading_label = QLabel(heading)
            heading_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
            self.body.addWidget(heading_label)
