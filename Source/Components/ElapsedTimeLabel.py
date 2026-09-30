import time
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel


def format_elapsed(seconds):
    """12.4 -> "12.4s", 75.2 -> "1m 15s", 3725 -> "1h 02m 05s\""""
    if seconds < 59.95:  # Anything higher would round up to "60.0s"
        return f"{seconds:.1f}s"
    minutes, secs = divmod(int(seconds), 60)
    if minutes < 60:
        return f"{minutes}m {secs:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes:02d}m {secs:02d}s"


class ElapsedTimeLabel(QLabel):
    """
    "⏱ Elapsed: 12.4s" label that ticks live while a process runs, then freezes on the final time.

    Usage:
        label = ElapsedTimeLabel()
        label.start(started_at)                  # started_at from time.monotonic(); defaults to now
        ...
        label.stop("Finished in")                # -> "⏱ Finished in 42.1s", returns the seconds
    Or show a fixed duration: ElapsedTimeLabel(seconds=42.1, prefix="Took")
    """

    def __init__(self, seconds=None, prefix="Elapsed:"):
        super().__init__()
        self.setStyleSheet("font-size: 10pt; font-weight: 600; color: #757575;")
        self.started_at = None
        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._tick)
        self._prefix = prefix

        self.set_elapsed(seconds or 0, prefix)

    def start(self, started_at=None):
        """Start ticking, counting from `started_at` (a time.monotonic() value; default: now)"""
        self.started_at = started_at if started_at is not None else time.monotonic()
        self._timer.start()
        self._tick()

    def stop(self, prefix=None):
        """Stop ticking and show the final time (optionally with a new prefix). Returns elapsed seconds."""
        self._timer.stop()
        seconds = self.elapsed()
        self.set_elapsed(seconds, prefix or self._prefix)
        return seconds

    def elapsed(self):
        return time.monotonic() - self.started_at if self.started_at is not None else 0

    def set_elapsed(self, seconds, prefix=None):
        """Show a fixed duration"""
        if prefix:
            self._prefix = prefix
        self.setText(f"⏱ {self._prefix} {format_elapsed(seconds)}")

    def _tick(self):
        self.set_elapsed(self.elapsed())
