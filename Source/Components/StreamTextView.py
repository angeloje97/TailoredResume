from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QTextEdit


class StreamTextView(QTextEdit):
    """Read-only monospace text view that streamed AI output is appended to."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 10pt;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)

    def append_chunk(self, text):
        """Append text at the end without adding a newline, keeping the view scrolled to the bottom"""
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)
        self.moveCursor(QTextCursor.End)
