from datetime import datetime, timedelta
from PySide6.QtWidgets import QHBoxLayout
from Components.StyledLineEdit import StyledLineEdit
from Components.StyledComboBox import StyledComboBox
from Components.AccentCheckbox import AccentCheckbox

SCORE_OPTIONS = ["1+", "2+", "3+", "4+", "5+", "6+", "7+", "8+", "9+", "10"]

# Date filter option -> days back from today (None = no date filter, 0 = today only)
DATE_OPTIONS = {"Any day": None, "Today": 0, "Last 3 Days": 3, "Last 7 Days": 7, "Last 30 Days": 30}


def filter_fields(data):
    """Extract the fields FilterBar.matches() checks from a saved application JSON"""
    job_data = data['Job']
    return {
        'position': job_data['Position Title'].lower(),
        'company': job_data['Company Name'].lower(),
        'tech_stack': ' '.join(job_data.get('Tech Stack', [])).lower(),
        'match_rating': float(job_data.get('Match Rating', 0)),
        'job_quality': float(job_data.get('Job Quality', 0)),
        'date_created': data['Meta']['Date Created'],
        'favorite': data['Meta'].get('Favorite', False),
        'save_submission': job_data.get('Save Submission', False)
    }


def build_filter_entries(datas):
    """
    Turn saved application JSONs into `{'data': data, **filter_fields(data)}` entries, newest first.

    Safe to run on a background thread (no Qt calls). Entries with missing/invalid fields are skipped.
    """
    entries = []
    for data in sorted(datas, key=lambda data: data['Meta'].get('Date Created', ''), reverse=True):
        try:
            entries.append({'data': data, **filter_fields(data)})
        except Exception:
            name = data.get('Meta', {}).get('File Name', '<unknown>')
            print(f"{'-'*50}\nCould not load item\n{name}\n{'-'*50}\n")
    return entries


class FilterBar(QHBoxLayout):
    """
    Search + filter controls row (search text, min match rating, min job quality, date range,
    and optional favorites / saved-submission toggles), combined with AND logic.

    Add it to a page with `layout.addLayout(filter_bar)`, then call `matches(filter_fields(data))`
    per item inside `on_filter_changed`.
    """

    def __init__(self, on_filter_changed, include_favorites=True, include_saved=True):
        super().__init__()
        self.setSpacing(10)

        # Search bar
        self.search_bar = StyledLineEdit("Search by position, company, or tech stack...",
                                         font_size=12, margin_y=15, on_change=on_filter_changed)
        self.addWidget(self.search_bar, stretch=3)

        # Dropdowns
        def dropdown(items):
            combo = StyledComboBox(items, on_change=on_filter_changed, font_size=12, margin_y=15, min_width=150)
            self.addWidget(combo, stretch=1)
            return combo

        self.min_rating = dropdown(["All Ratings"] + SCORE_OPTIONS)
        self.min_quality = dropdown(["All Quality"] + SCORE_OPTIONS)
        self.date_filter = dropdown(list(DATE_OPTIONS))

        # Optional favorites checkbox
        self.favorites = None
        if include_favorites:
            self.favorites = AccentCheckbox("⭐ Favorites", hover_border="#ffc107", hover_background="#fffde7",
                                            margin_y=15, on_change=on_filter_changed)
            self.addWidget(self.favorites, stretch=1)

        # Optional saved submissions checkbox
        self.saved = None
        if include_saved:
            self.saved = AccentCheckbox("📋 Saved", hover_border="#ff9800", hover_background="#fff3e0",
                                        margin_y=15, tooltip="Show only saved submissions (not applying)",
                                        on_change=on_filter_changed)
            self.addWidget(self.saved, stretch=1)

    def reset(self):
        """Clear the search text and set every filter back to its default"""
        self.search_bar.clear()
        self.min_rating.setCurrentIndex(0)
        self.min_quality.setCurrentIndex(0)
        self.date_filter.setCurrentIndex(0)
        if self.favorites:
            self.favorites.setChecked(False)
        if self.saved:
            self.saved.setChecked(False)

    def matches(self, item):
        """Whether an item (from filter_fields) passes every active filter"""
        query = self.search_bar.text().lower()
        if not (query in item['position'] or query in item['company'] or query in item['tech_stack']):
            return False

        if item['match_rating'] < self._min_score(self.min_rating):
            return False

        if item['job_quality'] < self._min_score(self.min_quality):
            return False

        days_back = DATE_OPTIONS[self.date_filter.currentText()]
        if days_back is not None:
            item_date = datetime.fromisoformat(item['date_created']).date()
            if item_date < (datetime.now() - timedelta(days=days_back)).date():
                return False

        if self.favorites and self.favorites.isChecked() and not item['favorite']:
            return False

        if self.saved and self.saved.isChecked() and not item['save_submission']:
            return False

        return True

    @staticmethod
    def _min_score(combo):
        # First option is "All ..." (no minimum); the rest are "X+" or "10"
        if combo.currentIndex() == 0:
            return 0
        return int(combo.currentText().rstrip('+'))
