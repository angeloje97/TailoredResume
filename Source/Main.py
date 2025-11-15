import sys
import asyncio
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QTextEdit,
                               QPushButton, QStackedWidget, QScrollArea)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
from Utility import json_template, full_base_resume_text,  resume_template, cover_letter_template, resume_prompt, paths
from Utility import save_json_obj, expand_list_to_keys, write_to_docx, clear_temp, save_document_temp, copy_temp_to_results, convert_temp_to_pdf, get_templates
from Agent import create_request, model
from datetime import datetime
import json


class AIWorker(QThread):
    """Worker thread for async AI requests"""
    finished = Signal(str)  # Signal to emit the response
    error = Signal(str)     # Signal to emit errors

    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        """Run the async request in a separate thread"""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the async function
            response = loop.run_until_complete(create_request(self.message))

            # Emit success signal
            self.finished.emit(response)

            loop.close()
        except Exception as e:
            # Emit error signal
            self.error.emit(str(e))


class ResumeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resume Tailor")
        self.setGeometry(100, 100, 1400, 650)

        # Create central widget and horizontal layout for sidebar + content
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_horizontal_layout = QHBoxLayout(central_widget)
        main_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        main_horizontal_layout.setSpacing(0)

        # Create sidebar
        self.create_sidebar(main_horizontal_layout)

        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        main_horizontal_layout.addWidget(self.stacked_widget)

        # Create the resume generation page
        self.create_resume_page()

        # Create the files/history page
        self.create_files_page()

        # Create the statistics page
        self.create_statistics_page()

        # Create the settings page
        self.create_settings_page()

    #region Pages

    def create_sidebar(self, parent_layout):
        """Create the left sidebar with navigation"""
        sidebar = QWidget()
        sidebar.setFixedWidth(80)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
            }
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 0)
        sidebar_layout.setSpacing(0)

        # Resume Generation button
        self.resume_btn = QPushButton("📄")
        self.resume_btn.setFixedSize(80, 80)
        self.resume_btn.setToolTip("Resume Generator")
        self.resume_btn.setStyleSheet("""
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
        self.resume_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        sidebar_layout.addWidget(self.resume_btn)

        # Files/History button
        self.files_btn = QPushButton("🗂️")
        self.files_btn.setFixedSize(80, 80)
        self.files_btn.setToolTip("Generated Resumes")
        self.files_btn.setStyleSheet("""
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
        self.files_btn.clicked.connect(self.show_files_page)
        sidebar_layout.addWidget(self.files_btn)

        # Statistics button
        self.stats_btn = QPushButton("📊")
        self.stats_btn.setFixedSize(80, 80)
        self.stats_btn.setToolTip("Statistics")
        self.stats_btn.setStyleSheet("""
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
        self.stats_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        sidebar_layout.addWidget(self.stats_btn)

        # Add stretch to push settings button to bottom
        sidebar_layout.addStretch()

        # Settings button
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(80, 80)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setStyleSheet("""
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
        self.settings_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        sidebar_layout.addWidget(self.settings_btn)

        parent_layout.addWidget(sidebar)

    def create_resume_page(self):
        """Create the resume generation page"""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        #Company Name Field
        company_name_label = QLabel("Company Name (Optional):")
        company_name_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        main_layout.addWidget(company_name_label)

        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("Enter the company name here...")
        self.company_name.setMinimumHeight(40)
        self.company_name.setStyleSheet("""
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
        main_layout.addWidget(self.company_name)

        # Job Title field
        title_label = QLabel("Job Title (Optional):")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        self.job_title = QLineEdit()
        self.job_title.setPlaceholderText("Enter the job title here...")
        self.job_title.setMinimumHeight(40)
        self.job_title.setStyleSheet("""
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
        main_layout.addWidget(self.job_title)

        # Job Description text box
        desc_label = QLabel("Job Description:")
        desc_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        main_layout.addWidget(desc_label)

        self.job_description = QTextEdit()
        self.job_description.setPlaceholderText("Paste the entire job description here...")
        self.job_description.setMinimumHeight(350)
        self.job_description.setStyleSheet("""
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
        main_layout.addWidget(self.job_description)

        # Generate button
        self.generate_button = QPushButton("Generate")
        self.generate_button.setMinimumHeight(50)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.generate_button.clicked.connect(self.on_generate)
        main_layout.addWidget(self.generate_button)

        # Add page to stacked widget
        self.stacked_widget.addWidget(page)

    #region History Page

    def create_files_page(self):
        """Create the files/history page container"""
        # Main page container
        self.files_page = QWidget()
        page_layout = QVBoxLayout(self.files_page)
        page_layout.setSpacing(0)
        page_layout.setContentsMargins(20, 20, 20, 0)

        # Title
        from Utility import get_json_datas

        count = len(get_json_datas())
        self.history_title_label = QLabel(f"History ({count} Results)")
        self.history_title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        page_layout.addWidget(self.history_title_label)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by position, company, or tech stack...")
        self.search_bar.setMinimumHeight(40)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 12pt;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                margin-top: 15px;
                margin-bottom: 15px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_history_items)
        page_layout.addWidget(self.search_bar)

        # Scrollable area for history items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        # Container widget for scrollable content
        scroll_content = QWidget()
        self.files_layout = QVBoxLayout(scroll_content)
        self.files_layout.setSpacing(15)
        self.files_layout.setContentsMargins(0, 0, 20, 20)

        scroll_area.setWidget(scroll_content)
        page_layout.addWidget(scroll_area)

        # Add page to stacked widget
        self.stacked_widget.addWidget(self.files_page)

    def show_files_page(self):
        """Refresh and show the files page"""
        from Utility import get_json_datas

        # Clear existing history items (keep the title and search bar)
        while self.files_layout.count() > 0:
            item = self.files_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Load fresh data
        datas = get_json_datas()
        datas = sorted(datas, key=lambda data: data['Meta']['Date Created'], reverse=True)

        # Update title with current count
        self.history_title_label.setText(f"History ({len(datas)} Results)")

        # Store history items with their data for filtering
        self.history_items = []
        self.history_widgets = []  # Track all widget instances for expansion management

        # Add history items
        for data in datas:
            job_data = data['Job']
            history_item = self.create_history_item(job_data)
            self.files_layout.addWidget(history_item)

            # Store widget reference
            self.history_widgets.append(history_item)

            # Store item with its searchable data
            self.history_items.append({
                'widget': history_item,
                'position': job_data['Position Title'].lower(),
                'company': job_data['Company Name'].lower(),
                'tech_stack': ' '.join(job_data['Tech Stack']).lower()
            })

        # Add stretch to push content to top
        self.files_layout.addStretch()

        # Clear search bar
        self.search_bar.clear()

        # Switch to files page
        self.stacked_widget.setCurrentIndex(1)

    def filter_history_items(self):
        """Filter history items based on search query"""
        query = self.search_bar.text().lower()

        for item_data in self.history_items:
            # Check if query matches position, company, or tech stack
            if (query in item_data['position'] or
                query in item_data['company'] or
                query in item_data['tech_stack']):
                item_data['widget'].setVisible(True)
            else:
                item_data['widget'].setVisible(False)

    def collapse_all_history_items(self, except_widget=None):
        """Collapse all history items except the specified one"""
        for widget in self.history_widgets:
            if widget != except_widget and hasattr(widget, 'is_expanded'):
                widget.is_expanded = False
                if hasattr(widget, 'details_widget'):
                    widget.details_widget.setVisible(False)

    #region History Item

    def create_history_item(self, job_data):
        """Create a history item widget"""
        # Destructure job data

        #region Main History Item
        position = job_data['Position Title']
        company = job_data['Company Name']
        start_date = job_data['Date Applied']
        end_date = job_data['Expected Response Date']
        tags = job_data.get('Tech Stack', None)
        salary = job_data.get('Salary', None)
        match_rating = int(job_data.get('Match Rating', 0))

        current_date = datetime.now()

        item_widget = QWidget()
        item_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
            }
            QWidget:hover {
                background-color: #fafafa;
            }
        """)
        item_widget.setCursor(Qt.CursorShape.PointingHandCursor)

        item_layout = QVBoxLayout(item_widget)
        item_layout.setSpacing(12)
        item_layout.setContentsMargins(20, 16, 20, 16)

        # Store expanded state
        item_widget.is_expanded = False

        # Header with position, company, salary, match rating, and date
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        position_company_label = QLabel(f"{position} at {company}")
        position_company_label.setStyleSheet("font-size: 15pt; font-weight: bold; color: #1a1a1a;")
        header_layout.addWidget(position_company_label)

        header_layout.addStretch()

        if salary:
            salary_label = QLabel(f"💰 {salary}")
            salary_label.setStyleSheet("""
                font-size: 10pt;
                color: #2e7d32;
                font-weight: 600;
                background-color: #e8f5e9;
                padding: 4px 10px;
                border-radius: 6px;
            """)
            header_layout.addWidget(salary_label)

        if match_rating is not None:
            # Determine color based on rating
            if match_rating >= 8:
                rating_color = "#2e7d32"  # Dark green
                rating_bg = "#e8f5e9"     # Light green bg
            elif match_rating >= 5:
                rating_color = "#ef6c00"  # Dark orange
                rating_bg = "#fff3e0"     # Light orange bg
            else:
                rating_color = "#c62828"  # Dark red
                rating_bg = "#ffebee"     # Light red bg

            match_label = QLabel(f"⭐ {match_rating}/10")
            match_label.setStyleSheet(f"""
                font-size: 10pt;
                color: {rating_color};
                font-weight: 600;
                background-color: {rating_bg};
                padding: 4px 10px;
                border-radius: 6px;
            """)
            header_layout.addWidget(match_label)

        # Date range label
        date_range_text = f"{start_date} - {end_date}"
        date_label = QLabel(date_range_text)

        # Parse dates and calculate elapsed time
        try:
            start_date_obj = datetime.strptime(start_date, "%m/%d/%y")
            end_date_obj = datetime.strptime(end_date, "%m/%d/%y")

            # Calculate total duration and elapsed time
            total_duration = (end_date_obj - start_date_obj).total_seconds()
            elapsed_time = (current_date - start_date_obj).total_seconds()

            # Calculate progress ratio
            if total_duration > 0:
                progress_ratio = elapsed_time / total_duration
            else:
                progress_ratio = 0

            # Determine color based on progress
            if progress_ratio < 0:
                # Not started yet - blue/gray
                date_label.setStyleSheet("""
                    font-size: 9pt;
                    color: #757575;
                    background-color: #f5f5f5;
                    padding: 4px 10px;
                    border-radius: 6px;
                """)
            elif progress_ratio < 1/3:
                # First third - green
                date_label.setStyleSheet("""
                    font-size: 9pt;
                    color: white;
                    background-color: #4CAF50;
                    padding: 4px 10px;
                    border-radius: 6px;
                    font-weight: bold;
                """)
            elif progress_ratio < 2/3:
                # Second third - yellow/orange
                date_label.setStyleSheet("""
                    font-size: 9pt;
                    color: white;
                    background-color: #FF9800;
                    padding: 4px 10px;
                    border-radius: 6px;
                    font-weight: bold;
                """)
            elif progress_ratio <= 1:
                # Final third - red
                date_label.setStyleSheet("""
                    font-size: 9pt;
                    color: white;
                    background-color: #f44336;
                    padding: 4px 10px;
                    border-radius: 6px;
                    font-weight: bold;
                """)
            else:
                # Past due - dark red
                date_label.setStyleSheet("""
                    font-size: 9pt;
                    color: white;
                    background-color: #c62828;
                    padding: 4px 10px;
                    border-radius: 6px;
                    font-weight: bold;
                """)
        except:
            # If date parsing fails, use default style
            date_label.setStyleSheet("""
                font-size: 9pt;
                color: #757575;
                background-color: #f5f5f5;
                padding: 4px 10px;
                border-radius: 6px;
            """)

        header_layout.addWidget(date_label)

        item_layout.addLayout(header_layout)

        # Tags
        if tags:
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(6)

            for tag in tags:
                tag_label = QLabel(tag)
                tag_label.setStyleSheet("""
                    QLabel {
                        background-color: #e3f2fd;
                        color: #1565c0;
                        padding: 5px 14px;
                        border-radius: 14px;
                        font-size: 9pt;
                        font-weight: 600;
                        border: 1px solid #bbdefb;
                    }
                """)
                tags_layout.addWidget(tag_label)

            tags_layout.addStretch()
            item_layout.addLayout(tags_layout)

        #endregion

        #region Expandable details

        # Expandable details section (initially hidden)

        description = job_data['Description']
        responsibilities = "\n".join(job_data['Responsibilities'])
        company_size = job_data['Company Size']
        job_quality_value = int(job_data.get('Job Quality', 5))  # Default to 5 if not provided
        job_quality_description = job_data.get('Job Quality Description', "NA")
        motive = job_data.get("Motive", "NA")

        details_widget = QWidget()
        details_widget.setVisible(False)
        details_layout = QVBoxLayout(details_widget)
        details_layout.setSpacing(10)
        details_layout.setContentsMargins(0, 10, 0, 0)

        # Prevent mouse events from propagating to parent
        details_widget.mousePressEvent = lambda e: e.accept()

        # Job Description
        job_desc_label = QLabel("Description:")
        job_desc_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #2c3e50;")
        job_desc_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_layout.addWidget(job_desc_label)

        job_desc_text = QLabel(f"{description}")
        job_desc_text.setStyleSheet("font-size: 10pt; color: #555; margin-left: 10px;")
        job_desc_text.setWordWrap(True)
        job_desc_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_layout.addWidget(job_desc_text)

        # Responsibilities
        responsibilities_label = QLabel("Responsibilities:")
        responsibilities_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #2c3e50; margin-top: 10px;")
        responsibilities_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_layout.addWidget(responsibilities_label)

        responsibilities_text = QLabel(f"{responsibilities}")
        responsibilities_text.setStyleSheet("font-size: 10pt; color: #555; margin-left: 10px;")
        responsibilities_text.setWordWrap(True)
        responsibilities_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_layout.addWidget(responsibilities_text)

        # Company Size (horizontal layout)
        company_size_layout = QHBoxLayout()
        company_size_layout.setSpacing(10)
        company_size_layout.setContentsMargins(0, 10, 0, 0)

        company_size_label = QLabel("Company Size:")
        company_size_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #2c3e50;")
        company_size_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        company_size_layout.addWidget(company_size_label)

        company_size_text = QLabel(f"{company_size}")
        company_size_text.setStyleSheet("font-size: 10pt; color: #555;")
        company_size_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        company_size_layout.addWidget(company_size_text)

        company_size_layout.addStretch()
        details_layout.addLayout(company_size_layout)

        # Job Quality (horizontal layout with colored tag)
        job_quality_layout = QHBoxLayout()
        job_quality_layout.setSpacing(10)
        job_quality_layout.setContentsMargins(0, 10, 0, 0)

        job_quality_label = QLabel("Job Quality:")
        job_quality_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #2c3e50;")
        job_quality_layout.addWidget(job_quality_label)

        # Get job quality value and determine color

        # Determine color based on numeric quality value (1-10)
        if job_quality_value >= 8:
            quality_color = "#4CAF50"  # Green (8-10)
            quality_bg = "#e8f5e9"
        elif job_quality_value >= 5:
            quality_color = "#FF9800"  # Orange (5-7)
            quality_bg = "#fff3e0"
        else:
            quality_color = "#f44336"  # Red (1-4)
            quality_bg = "#ffebee"

        job_quality_tag = QLabel(f"{job_quality_value}/10")
        job_quality_tag.setStyleSheet(f"""
            font-size: 10pt;
            color: {quality_color};
            font-weight: 600;
            background-color: {quality_bg};
            padding: 4px 12px;
            border-radius: 12px;
        """)
        job_quality_layout.addWidget(job_quality_tag)

        job_quality_layout.addStretch()
        details_layout.addLayout(job_quality_layout)

        # Job Quality Description
        job_quality_desc_label = QLabel("Job Quality Description:")
        job_quality_desc_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #2c3e50; margin-top: 10px;")
        job_quality_desc_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_layout.addWidget(job_quality_desc_label)

        job_quality_desc_text = QLabel(f"{job_quality_description}")
        job_quality_desc_text.setStyleSheet("font-size: 10pt; color: #555; margin-left: 10px;")
        job_quality_desc_text.setWordWrap(True)
        job_quality_desc_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_layout.addWidget(job_quality_desc_text)

        # Motive
        motive_label = QLabel("Why Work Here:")
        motive_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #2c3e50; margin-top: 10px;")
        motive_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_layout.addWidget(motive_label)

        motive_text = QLabel(f"{motive}")
        motive_text.setStyleSheet("font-size: 10pt; color: #555; margin-left: 10px;")
        motive_text.setWordWrap(True)
        motive_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_layout.addWidget(motive_text)

        item_layout.addWidget(details_widget)

        # Store reference to details widget for toggling
        item_widget.details_widget = details_widget

        # Add click event to toggle expansion
        def toggle_expand(event):
            # Collapse all other items first
            self.collapse_all_history_items(except_widget=item_widget)

            # Toggle this item
            item_widget.is_expanded = not item_widget.is_expanded
            details_widget.setVisible(item_widget.is_expanded)

        item_widget.mousePressEvent = toggle_expand

        return item_widget
        
        #endregion

    #endregion

    #endregion

    def create_statistics_page(self):
        """Create the statistics page"""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Statistics")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Placeholder content
        info_label = QLabel("This page will show application statistics and charts.")
        info_label.setStyleSheet("font-size: 12pt; color: #666;")
        main_layout.addWidget(info_label)

        # Add stretch to push content to top
        main_layout.addStretch()

        # Add page to stacked widget
        self.stacked_widget.addWidget(page)

    def create_settings_page(self):
        """Create the settings page"""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Settings")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Placeholder content
        info_label = QLabel("This page will contain application settings.")
        info_label.setStyleSheet("font-size: 12pt; color: #666;")
        main_layout.addWidget(info_label)

        # Add stretch to push content to top
        main_layout.addStretch()

        # Add page to stacked widget
        self.stacked_widget.addWidget(page)

    #endregion


    def on_generate(self):
        """Handle the generate button click"""
        job_title = self.job_title.text()
        company_name = self.company_name.text()
        job_desc = self.job_description.toPlainText()

        # Disable button while processing
        self.generate_button.setEnabled(False)
        self.generate_button.setText("Generating...")

        # Reload templates and prompts
        get_templates()
        from Utility import resume_prompt, json_template, full_base_resume_text

        current_date_time = datetime.now().strftime("%B %d, %Y %I:%M %p")
        

        # Build the AI prompt
        message = f"My resumes:\n{full_base_resume_text}\n"
        message += f"Company Name: {company_name}\n Job Title: {job_title}\n Job Description: {job_desc}\n"
        message += f"{resume_prompt}"
        message += f"Please respond in a parsable json format that looks like this: \n{json.dumps(json_template)}\n"
        message += f"Also make sure to fillout the cover page. The time this request was made is {current_date_time}"


        # Store company name for use in callback
        self.current_company_name = company_name

        # Create and start worker thread
        self.worker = AIWorker(message)
        self.worker.finished.connect(self.on_ai_response)
        self.worker.error.connect(self.on_ai_error)
        self.worker.start()

    def on_ai_response(self, response):
        """Handle successful AI response"""
        try:
            data = json.loads(response)
            
            meta = data['Meta']

            clear_temp()

            self.generate_button.setText("Processing Documents...")
            
            resume_data = expand_list_to_keys(data['Resume'], "")
            cover_letter_data = data['CoverLetter']

            resume_name = resume_data['File Name']
            cover_letter_name = cover_letter_data['File Name']
            #region Editing Meta Data

            current_date_time = datetime.now()

            data['Meta']['Resume Path'] = str(paths['results'] / f"{resume_name}.docx")
            data['Meta']['Cover Letter Path'] = str(paths['results'] / f"{cover_letter_name}.docx")
            data['Meta']['Model Used'] = model
            data['Meta']['Date Created'] = current_date_time.isoformat()
            #endregion

            # clear_temp()

            job = data['Job']
            save_json_obj(expand_list_to_keys(data, ""), f"{job['Position Title']} {job['Company Name']}")
            #region Filling Documents
            

            resume_doc = write_to_docx(resume_template, resume_data)
            cover_letter_doc = write_to_docx(cover_letter_template, cover_letter_data)

            save_document_temp(resume_doc, resume_name)
            save_document_temp(cover_letter_doc, cover_letter_name)

            convert_temp_to_pdf()

            copy_temp_to_results()


            #endregion

            # Re-enable button
            self.generate_button.setEnabled(True)
            self.generate_button.setText("Generate Resume")

            print("Resume generated successfully!")
        except Exception as e:
            self.on_ai_error(str(e))

    def on_ai_error(self, error_msg):
        """Handle AI request errors"""
        print(f"Error: {error_msg}")

        # Re-enable button
        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generate Resume")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResumeApp()
    window.show()
    sys.exit(app.exec())
