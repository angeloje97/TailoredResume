from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from Components.ActionBarButton import ActionBarButton
from Components.RatingBadge import RatingBadge
from Components.DateRangeBadge import DateRangeBadge


class ArchiveItem(QWidget):
    """
    Compact single-row card for a saved application: position/company, ratings, dates,
    and optional Restore / Delete buttons.

    Args:
        data: Application JSON (Meta/Job/...)
        on_restore: Called with `data` when Restore is clicked (default: None, button hidden)
        on_delete: Called with `data` when Delete is clicked (default: None, button hidden)
    """

    def __init__(self, data, on_restore=None, on_delete=None):
        super().__init__()
        self.data = data
        self.on_restore = on_restore
        self.on_delete = on_delete
        self._build_ui()

    def _build_ui(self):
        data = self.data
        job_data = data['Job']

        # Extract data
        company = job_data['Company Name']
        position = job_data['Position Title']
        date_applied = job_data.get('Date Applied', "N/A")
        expected_response = job_data.get('Expected Response Date', "N/A")
        match_rating = job_data.get('Match Rating', 0)
        job_quality = job_data.get('Job Quality', 5)

        try:
            match_rating = float(match_rating)
        except:
            match_rating = 5.0

        try:
            job_quality = float(job_quality)
        except:
            job_quality = 5.0

        # QWidget subclasses only paint their stylesheet background with this set
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: none;
                border-radius: 8px;
            }
        """)

        item_layout = QHBoxLayout(self)
        item_layout.setSpacing(16)
        item_layout.setContentsMargins(20, 12, 20, 12)

        # Company name label
        company_label = QLabel(f"{position} at {company}")
        company_label.setStyleSheet("font-size: 13pt; font-weight: bold; color: #1a1a1a;")
        item_layout.addWidget(company_label)

        item_layout.addStretch()

        item_layout.addWidget(RatingBadge("💎", job_quality, font_size=9))
        item_layout.addWidget(RatingBadge("⭐", match_rating, font_size=9))

        # Date range label (applied - expected response)
        item_layout.addWidget(DateRangeBadge(date_applied, expected_response, show_progress=False))

        # Restore button
        if self.on_restore:
            def on_restore_click(event):
                event.accept()
                self.on_restore(data)

            item_layout.addWidget(ActionBarButton("↩️", "Restore", on_restore_click))

        # Delete button
        if self.on_delete:
            def on_delete_click(event):
                event.accept()
                self.on_delete(data)

            item_layout.addWidget(ActionBarButton("🗑️", "Delete", on_delete_click,
                                                  hover_color="#ffebee", hover_border="#f44336", pressed_color="#ffcdd2"))
