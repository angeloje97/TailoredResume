from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame

DONE_COLOR = "#4CAF50"
CURRENT_COLOR = "#2196F3"
PENDING_COLOR = "#bdbdbd"
PENDING_LABEL_COLOR = "#9e9e9e"
CURRENT_LABEL_COLOR = "#1a1a1a"


class StageTimeline(QWidget):
    """Horizontal stepper showing progress through a sequence of named stages."""

    def __init__(self, stages, parent=None):
        super().__init__(parent)
        self.stages = stages
        self.current_stage = -1
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        labels_row = QHBoxLayout()
        labels_row.setSpacing(0)
        self.stage_labels = []
        for stage in self.stages:
            label = QLabel(stage)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            labels_row.addWidget(label, 1)
            self.stage_labels.append(label)
        outer.addLayout(labels_row)

        line_row = QHBoxLayout()
        line_row.setSpacing(0)
        line_row.setContentsMargins(0, 0, 0, 0)

        self.nodes = []
        self.segments = []
        for i in range(len(self.stages)):
            node = QLabel("●")
            node.setFixedWidth(20)
            node.setAlignment(Qt.AlignmentFlag.AlignCenter)
            line_row.addWidget(node)
            self.nodes.append(node)

            if i < len(self.stages) - 1:
                segment = QFrame()
                segment.setFixedHeight(4)
                line_row.addWidget(segment, 1)
                self.segments.append(segment)

        outer.addLayout(line_row)

        self._render()

    def set_stage(self, index):
        """Advance the timeline so stages before `index` are complete and `index` is active."""
        self.current_stage = index
        self._render()

    def complete(self):
        """Mark every stage as complete (final success state)."""
        self.current_stage = len(self.stages)
        self._render()

    def _render(self):
        for i, (label, node) in enumerate(zip(self.stage_labels, self.nodes)):
            if i < self.current_stage:
                label.setStyleSheet(f"font-size: 9pt; font-weight: 600; color: {DONE_COLOR};")
                node.setStyleSheet(f"color: {DONE_COLOR}; font-size: 14pt;")
            elif i == self.current_stage:
                label.setStyleSheet(f"font-size: 9pt; font-weight: 700; color: {CURRENT_LABEL_COLOR};")
                node.setStyleSheet(f"color: {CURRENT_COLOR}; font-size: 18pt;")
            else:
                label.setStyleSheet(f"font-size: 9pt; font-weight: 600; color: {PENDING_LABEL_COLOR};")
                node.setStyleSheet(f"color: {PENDING_COLOR}; font-size: 14pt;")

        for i, segment in enumerate(self.segments):
            color = DONE_COLOR if i < self.current_stage else "#e0e0e0"
            segment.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
