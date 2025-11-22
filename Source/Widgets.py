from PySide6.QtWidgets import (QPushButton)

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