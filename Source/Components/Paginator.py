import math
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from Components.StyledComboBox import StyledComboBox
from Components.ActionBarButton import action_bar_button_style

PAGE_SIZES = [10, 25, 50, 100]


class Paginator(QWidget):
    """
    "Show [10|25|50|100]   ◀  Page 2 of 16 · 26-50 of 379  ▶" control.

    Call `set_total(n)` whenever the list being paged changes, and render `slice(items)`
    when `page_changed` fires. If `key_target` is given, the Left/Right arrow keys pressed
    anywhere inside it (outside of text inputs) also go to the previous/next page.
    """
    page_changed = Signal()

    def __init__(self, key_target=None, page_size=25):
        super().__init__()
        self.page = 0
        self.total = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(8)

        show_label = QLabel("Show:")
        show_label.setStyleSheet("font-size: 11pt; color: #333;")
        layout.addWidget(show_label)

        self.page_size_combo = StyledComboBox([str(size) for size in PAGE_SIZES], current=str(page_size),
                                              on_change=self._on_page_size_changed, min_width=90)
        layout.addWidget(self.page_size_combo)
        self._page_size = page_size

        layout.addStretch()

        self.prev_button = self._arrow_button("◀", "Previous page (Left arrow)", self.prev_page)
        layout.addWidget(self.prev_button)

        self.range_label = QLabel()
        self.range_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.range_label.setMinimumWidth(220)
        self.range_label.setStyleSheet("font-size: 11pt; color: #333;")
        layout.addWidget(self.range_label)

        self.next_button = self._arrow_button("▶", "Next page (Right arrow)", self.next_page)
        layout.addWidget(self.next_button)

        if key_target is not None:
            # Clicking empty space in the page takes focus off the search bar so the arrow keys reach us
            key_target.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            key_target.installEventFilter(self)

        self._refresh()

    @staticmethod
    def _arrow_button(icon, tooltip, on_click):
        button = QPushButton(icon)
        button.setFixedSize(36, 36)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip(tooltip)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setStyleSheet(action_bar_button_style("white", "#e0e0e0", "#e3f2fd", "#2196F3", "#bbdefb")
                             + "QPushButton:disabled { color: #bdbdbd; background-color: #fafafa; }")
        button.clicked.connect(on_click)
        return button

    @property
    def page_size(self):
        return self._page_size

    @property
    def page_count(self):
        return max(1, math.ceil(self.total / self._page_size))

    def set_total(self, total):
        """Update the number of items being paged, keeping the current page when it still exists"""
        self.total = total
        self.page = min(self.page, self.page_count - 1)
        self._refresh()

    def reset(self):
        """Go back to the first page (without emitting page_changed)"""
        self.page = 0
        self._refresh()

    def slice(self, items):
        """Return the items on the current page"""
        start = self.page * self._page_size
        return items[start:start + self._page_size]

    def next_page(self):
        if self.page < self.page_count - 1:
            self.page += 1
            self._refresh()
            self.page_changed.emit()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self._refresh()
            self.page_changed.emit()

    def _on_page_size_changed(self, text):
        # Stay on the page that contains the first item currently shown
        first_index = self.page * self._page_size
        self._page_size = int(text)
        self.page = first_index // self._page_size
        self._refresh()
        self.page_changed.emit()

    def _refresh(self):
        if self.total == 0:
            self.range_label.setText("No results")
        else:
            start = self.page * self._page_size + 1
            end = min(start + self._page_size - 1, self.total)
            self.range_label.setText(f"Page {self.page + 1} of {self.page_count} · {start}-{end} of {self.total}")

        self.prev_button.setEnabled(self.page > 0)
        self.next_button.setEnabled(self.page < self.page_count - 1)

    def eventFilter(self, obj, event):
        # Key presses the focused child didn't handle (e.g. not a cursor move in the search bar) bubble up here
        if event.type() == QEvent.Type.KeyPress and event.modifiers() == Qt.KeyboardModifier.NoModifier:
            if event.key() == Qt.Key.Key_Left:
                self.prev_page()
                return True
            if event.key() == Qt.Key.Key_Right:
                self.next_page()
                return True
        return False
