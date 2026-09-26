from PySide6.QtWidgets import QLabel, QLineEdit


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
