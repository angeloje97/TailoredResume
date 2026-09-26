from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel


class ScrollList(QScrollArea):
    """Borderless scroll area wrapping a vertical list layout (`self.list_layout`)."""

    def __init__(self, spacing=15, margins=(0, 0, 0, 0), background=None, align_top=False):
        super().__init__()
        self.setWidgetResizable(True)
        self.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                {f"background-color: {background};" if background else ""}
            }}
        """)

        container = QWidget()
        self.list_layout = QVBoxLayout(container)
        self.list_layout.setSpacing(spacing)
        self.list_layout.setContentsMargins(*margins)
        if align_top:
            self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setWidget(container)

        # Don't swallow arrow keys, so a Paginator on the parent page can use them
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def add(self, widget):
        self.list_layout.addWidget(widget)

    def clear(self):
        """Remove and delete every item in the list"""
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                # Hide now, since deleteLater only takes effect on the next event loop pass
                item.widget().hide()
                item.widget().deleteLater()

    def show_message(self, text):
        """Replace the list contents with a gray status message (e.g. "Loading...", "No results")"""
        self.clear()
        message = QLabel(text)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("font-size: 12pt; color: #9e9e9e; padding: 40px;")
        self.add(message)

    def scroll_to_top(self):
        self.verticalScrollBar().setValue(0)
