from PySide6.QtWidgets import (QPushButton, QLabel, QLineEdit, QTextEdit, QHBoxLayout)
from PySide6.QtCore import Qt

def ActionBarButton(icon, tooltip, on_click, hover_color="#e3f2fd", hover_border="#2196F3", pressed_color="#bbdefb"):
    """
    Create a consistent action bar button with icon

    Args:
        icon: Emoji or text to display
        tooltip: Tooltip text
        on_click: Callback function that takes an event parameter
        hover_color: Background color on hover (default: light blue)
        hover_border: Border color on hover (default: blue)
        pressed_color: Background color when pressed (default: darker blue)

    Returns:
        QPushButton configured for action bar
    """
    button = QPushButton(icon)
    button.setFixedSize(32, 32)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setToolTip(tooltip)
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14pt;
            padding: 0px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
            border: 1px solid {hover_border};
        }}
        QPushButton:pressed {{
            background-color: {pressed_color};
        }}
    """)
    button.mousePressEvent = on_click

    return button

def ToggleActionBarButton(icon, tooltip, is_active, active_bg="#4CAF50", active_border="#4CAF50",
                          active_hover="#45a049", active_pressed="#3d8b40",
                          inactive_hover="#fffde7", inactive_border="#ffc107", inactive_pressed="#fff9c4"):
    """
    Create a toggle action bar button with two states (active/inactive)

    Args:
        icon: Emoji or text to display
        tooltip: Tooltip text
        is_active: Initial active state (True/False)
        active_bg: Background color when active (default: green)
        active_border: Border color when active (default: green)
        active_hover: Hover color when active (default: dark green)
        active_pressed: Pressed color when active (default: darker green)
        inactive_hover: Hover color when inactive (default: light yellow)
        inactive_border: Border color on hover when inactive (default: yellow)
        inactive_pressed: Pressed color when inactive (default: lighter yellow)

    Returns:
        tuple: (button, update_style_function)
            - button: QPushButton configured for action bar
            - update_style_function: Function to call with boolean to update style
    """
    button = QPushButton(icon)
    button.setFixedSize(32, 32)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setToolTip(tooltip)

    def update_style(is_active):
        if is_active:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {active_bg};
                    border: 1px solid {active_border};
                    border-radius: 6px;
                    font-size: 14pt;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: {active_hover};
                    border: 1px solid {active_hover};
                }}
                QPushButton:pressed {{
                    background-color: {active_pressed};
                }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    font-size: 14pt;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: {inactive_hover};
                    border: 1px solid {inactive_border};
                }}
                QPushButton:pressed {{
                    background-color: {inactive_pressed};
                }}
            """)

    # Set initial style
    update_style(is_active)

    return button, update_style

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