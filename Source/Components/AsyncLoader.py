from PySide6.QtCore import QThread, Signal


class AsyncLoader(QThread):
    """
    Run a blocking function (e.g. reading JSON files from disk) on a background thread.

    Connect `loaded` / `failed` to methods of a QWidget so the slot runs back on the GUI thread.
    The loader deletes itself once finished, so pass a parent to keep it alive while running.
    """
    loaded = Signal(object)  # Emits the function's return value
    failed = Signal(str)     # Emits the error message

    def __init__(self, load_fn, parent=None):
        super().__init__(parent)
        self.load_fn = load_fn
        self.finished.connect(self.deleteLater)

    def run(self):
        try:
            self.loaded.emit(self.load_fn())
        except Exception as e:
            self.failed.emit(str(e))
