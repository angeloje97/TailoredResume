from PySide6.QtWidgets import QLabel, QTextEdit


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
