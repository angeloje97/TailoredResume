from PySide6.QtWidgets import (QPushButton, QLabel, QLineEdit, QTextEdit, QHBoxLayout)
from PySide6.QtCore import Qt

def SideBarButton(label, tooltip, on_click):
    button = QPushButton(label)
    button.setFixedSize(80, 80)
    button.setToolTip(tooltip)
    button.setStyleSheet("""
        QPushButton {
            background-color: #34495e;
            color: white;
            font-size: 32pt;
            border: none;
            border-left: 4px solid #2c3e50;
        }
        QPushButton:hover {
            background-color: #4CAF50;
            border-left: 4px solid #4CAF50;
        }
        QPushButton:pressed {
            background-color: #45a049;
        }
    """)
    button.clicked.connect(lambda: on_click())

    return button

def InputText(label, layout_obj, placeholder="", height=40):
    title_label = QLabel(label)
    title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
    layout_obj.addWidget(title_label)

    job_title = QLineEdit()
    job_title.setPlaceholderText(placeholder)
    job_title.setMinimumHeight(height)
    job_title.setStyleSheet("""
        QLineEdit {
            padding: 8px;
            font-size: 12pt;
            border: 2px solid #cccccc;
            border-radius: 5px;
        }
        QLineEdit:focus {
            border: 2px solid #4CAF50;
        }
    """)
    layout_obj.addWidget(job_title)

    return job_title

def InputTextBox(label, layout_obj, placeholder = "", height=350):

    if(len(label) > 0):
        desc_label = QLabel(label)
        desc_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout_obj.addWidget(desc_label)
        

    job_description = QTextEdit()
    job_description.setPlaceholderText(placeholder)
    job_description.setMinimumHeight(height)
    job_description.setStyleSheet("""
        QTextEdit {
            padding: 10px;
            font-size: 11pt;
            border: 2px solid #cccccc;
            border-radius: 5px;
        }
        QTextEdit:focus {
            border: 2px solid #4CAF50;
        }
    """)
    layout_obj.addWidget(job_description)

    return job_description

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