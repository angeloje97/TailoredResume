from PySide6.QtWidgets import QWidget, QVBoxLayout
from Components.PageTitle import PageTitle
from Components.FilterBar import FilterBar, build_filter_entries
from Components.ScrollList import ScrollList
from Components.Paginator import Paginator
from Components.AsyncLoader import AsyncLoader


class PagedListPage(QWidget):
    """
    Base for pages that list saved applications (History, Archive): title, FilterBar,
    a paged ScrollList, and a Paginator. Data is loaded off the GUI thread, then filtered
    and paged in memory; only the current page's item widgets are ever built.

    Subclasses implement:
        load_datas()        -> list of application JSONs (runs on a background thread, no Qt calls)
        create_item(data)   -> QWidget for one application
    and may override title_text() to customize the result count shown in the title.
    """

    def __init__(self, stacked_widget, title, include_favorites=True, include_saved=True,
                 list_spacing=15, list_margins=(0, 0, 20, 20), list_background=None):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.title = title

        self.entries = []       # Every loaded entry: {'data': ..., **filter_fields(data)}
        self.filtered = []      # Entries passing the current filters
        self.item_widgets = []  # Widgets on the current page
        self._loading = False
        self._loader = None

        page_layout = QVBoxLayout(self)
        page_layout.setSpacing(0)
        page_layout.setContentsMargins(20, 20, 20, 0)

        self.title_label = PageTitle(title)
        page_layout.addWidget(self.title_label)

        self.filter_bar = FilterBar(on_filter_changed=self._on_filter_changed,
                                    include_favorites=include_favorites, include_saved=include_saved)
        page_layout.addLayout(self.filter_bar)

        self.item_list = ScrollList(spacing=list_spacing, margins=list_margins,
                                    background=list_background, align_top=True)
        page_layout.addWidget(self.item_list)

        self.paginator = Paginator(key_target=self)
        self.paginator.page_changed.connect(self.render_page)
        page_layout.addWidget(self.paginator)

    #region Subclass hooks

    def load_datas(self):
        raise NotImplementedError

    def create_item(self, data):
        raise NotImplementedError

    def title_text(self):
        return f"{self.title} ({len(self.filtered)} Results)"

    #endregion

    def show_page(self):
        """Switch to this page with filters and paging reset, then reload its data"""
        self.stacked_widget.setCurrentWidget(self)
        self.setFocus()

        # Suppress the filter callbacks reset() fires, since the data is about to be replaced
        self._loading = True
        self.filter_bar.reset()
        self.paginator.reset()
        self.reload()

    def reload(self):
        """Re-read the data in the background, keeping the current filters and page"""
        self._loading = True
        self.title_label.setText(f"{self.title} (Loading...)")
        self.item_list.show_message("Loading...")

        self._loader = AsyncLoader(lambda: build_filter_entries(self.load_datas()), self)
        self._loader.loaded.connect(self._on_loaded)
        self._loader.failed.connect(self._on_load_failed)
        self._loader.start()

    def _on_loaded(self, entries):
        # Ignore results from an older load that finished after a newer one started
        if self.sender() is not self._loader:
            return
        self._loading = False
        self.entries = entries
        self.apply_filters(reset_page=False)

    def _on_load_failed(self, error_message):
        if self.sender() is not self._loader:
            return
        self._loading = False
        self.title_label.setText(f"{self.title} (Failed to load)")
        self.item_list.show_message(f"Could not load files: {error_message}")

    def _on_filter_changed(self, *_):
        self.apply_filters()

    def apply_filters(self, reset_page=True):
        """Recompute which entries pass the filters, then show the first (or current) page"""
        if self._loading:
            return

        self.filtered = [entry for entry in self.entries if self.filter_bar.matches(entry)]
        self.title_label.setText(self.title_text())

        if reset_page:
            self.paginator.reset()
        self.paginator.set_total(len(self.filtered))
        self.render_page()

    def render_page(self):
        """Build widgets for the current page only"""
        self.item_list.clear()
        self.item_widgets = []

        page_entries = self.paginator.slice(self.filtered)
        if not page_entries:
            self.item_list.show_message("No results")
            return

        for entry in page_entries:
            try:
                widget = self.create_item(entry['data'])
            except Exception:
                print(f"{'-'*50}\nCould not create item\n{entry['data']['Meta'].get('File Name')}\n{'-'*50}\n")
                continue
            self.item_list.add(widget)
            self.item_widgets.append(widget)

        self.item_list.scroll_to_top()

    def find_entry(self, data):
        """The loaded entry for a given application JSON (to update its filter fields after an edit)"""
        return next((entry for entry in self.entries if entry['data'] is data), None)
