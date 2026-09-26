from PySide6.QtWidgets import QLabel, QHBoxLayout
from PySide6.QtCore import Qt


def LabelDescription(label_text, description_text, layout_obj, inline=False):

    company_size_layout = QHBoxLayout()
    company_size_layout.setSpacing(10)
    company_size_layout.setContentsMargins(0, 10, 0, 0)

    label = QLabel(label_text)
    label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #2c3e50; margin-top: 10px;")
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    text = QLabel(description_text)
    text.setStyleSheet("font-size: 10pt; color: #555; margin-left: 10px;")
    text.setWordWrap(True)
    text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    if not inline:
        layout_obj.addWidget(label)
        layout_obj.addWidget(text)
    else:
        company_size_layout.addWidget(label)
        company_size_layout.addWidget(text)
        company_size_layout.addStretch()
        layout_obj.addLayout(company_size_layout)

    return [label, text]
