import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QTextEdit,
                               QPushButton, QStackedWidget, QScrollArea, QComboBox, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from Utility import paths, get_config, update_config


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

        # Create the archive page
        self.create_archive_page()

        # Create the statistics page
        self.create_statistics_page()

        # Create the settings page
        self.create_settings_page()

    #region Pages

    def create_sidebar(self, parent_layout):
        """Create the left sidebar with navigation"""

        from Widgets import SideBarButton
        
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

        self.resume_btn = SideBarButton("📄", "Resume Generator", lambda: self.stacked_widget.setCurrentIndex(0))
        sidebar_layout.addWidget(self.resume_btn)

        self.files_btn = SideBarButton("🗂️", "History", self.show_files_page)
        sidebar_layout.addWidget(self.files_btn)

        # Archive button
        self.archive_btn = SideBarButton("📦", "Archive", self.show_archive_page)
        sidebar_layout.addWidget(self.archive_btn)

        # Statistics button
        self.stats_btn = SideBarButton("📊", "Statistics", lambda: self.stacked_widget.setCurrentIndex(3))
        sidebar_layout.addWidget(self.stats_btn)

        # Add stretch to push settings button to bottom
        sidebar_layout.addStretch()

        # Settings button
        self.settings_btn = SideBarButton("⚙️", "Settings", lambda: self.stacked_widget.setCurrentIndex(4))
        sidebar_layout.addWidget(self.settings_btn)

        parent_layout.addWidget(sidebar)

    #region Resume Page

    def create_resume_page(self):
        """Create the resume generation page and add it to the stacked widget"""
        from Pages.Resume.Index import ResumePage

        self.resume_page = ResumePage()
        self.stacked_widget.addWidget(self.resume_page)

    #endregion

    #region History Page

    def create_files_page(self):
        """Create the files/history page and add it to the stacked widget"""
        from Pages.History.Index import FilesPage

        self.files_page = FilesPage(self.stacked_widget)
        self.stacked_widget.addWidget(self.files_page)

    def show_files_page(self):
        """Refresh and show the files page"""
        self.files_page.show_files_page()

    #endregion

    #region Archive Page

    def create_archive_page(self):
        """Create the archive page container"""
        self.archive_page = QWidget()
        page_layout = QVBoxLayout(self.archive_page)
        page_layout.setSpacing(0)
        page_layout.setContentsMargins(20, 20, 20, 0)

        # Title
        self.archive_title_label = QLabel("Archive (0 Results)")
        self.archive_title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        page_layout.addWidget(self.archive_title_label)

        # Create filter bar using reusable component
        from Widgets import FilterBar
        filters = FilterBar(on_filter_changed=self.filter_archive_items,
                           include_favorites=False, include_saved=False)
        page_layout.addLayout(filters['layout'])

        # Store references to filter widgets
        self.archive_search_bar = filters['search_bar']
        self.archive_min_rating_combo = filters['min_rating']
        self.archive_min_quality_combo = filters['min_quality']
        self.archive_date_filter_combo = filters['date_filter']

        # Create scroll area for archived items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
        """)

        # Container for archived items
        self.archive_container = QWidget()
        self.archive_layout = QVBoxLayout(self.archive_container)
        self.archive_layout.setSpacing(12)
        self.archive_layout.setContentsMargins(0, 15, 0, 20)
        self.archive_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(self.archive_container)
        page_layout.addWidget(scroll_area)

        # Add page to stacked widget
        self.stacked_widget.addWidget(self.archive_page)

    def show_archive_page(self):
        """Refresh and show the archive page"""
        from Utility import get_archived_datas

        # Clear existing items
        while self.archive_layout.count():
            item = self.archive_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Load archived data
        archived_datas = sorted(get_archived_datas(), key=lambda data: data['Meta']['Date Created'], reverse=True )

        # Update title with count
        self.archive_title_label.setText(f"Archive ({len(archived_datas)} Results)")

        # Store archive items with searchable data for filtering
        self.archive_items = []

        # Create archive items
        for data in archived_datas:
            try:
                job_data = data['Job']
                archive_item = self.create_archive_item(data)
                self.archive_layout.addWidget(archive_item)

                # Store item with its searchable data
                self.archive_items.append({
                    'widget': archive_item,
                    'position': job_data['Position Title'].lower(),
                    'company': job_data['Company Name'].lower(),
                    'tech_stack': ' '.join(job_data.get('Tech Stack', [])).lower(),
                    'match_rating': float(job_data.get('Match Rating', 0)),
                    'job_quality': float(job_data.get('Job Quality', 0)),
                    'date_created': data['Meta']['Date Created']
                })
            except Exception as e:
                name = data['Meta']['File Name']
                print(f"{'-'*50}\nCould not create archived item\n{name}\n{'-'*50}\n")

        # Clear search bar and reset filters
        self.archive_search_bar.clear()
        self.archive_min_rating_combo.setCurrentIndex(0)
        self.archive_min_quality_combo.setCurrentIndex(0)
        self.archive_date_filter_combo.setCurrentIndex(0)

        # Switch to archive page
        self.stacked_widget.setCurrentIndex(2)

    def filter_archive_items(self):
        """Filter archive items based on search query, minimum rating, minimum job quality, and date range"""
        from datetime import datetime, timedelta

        query = self.archive_search_bar.text().lower()

        # Get minimum rating filter
        rating_text = self.archive_min_rating_combo.currentText()
        if rating_text == "All Ratings":
            min_rating = 0
        else:
            # Extract number from "X+" format
            min_rating = int(rating_text.rstrip('+'))

        # Get minimum job quality filter
        quality_text = self.archive_min_quality_combo.currentText()
        if quality_text == "All Quality":
            min_quality = 0
        else:
            # Extract number from "X+" format
            min_quality = int(quality_text.rstrip('+'))

        # Get date filter
        date_filter_text = self.archive_date_filter_combo.currentText()
        if date_filter_text == "Any day":
            date_cutoff = None
        elif date_filter_text == "Today":
            date_cutoff = datetime.now().date()
        elif date_filter_text == "Last 3 Days":
            date_cutoff = (datetime.now() - timedelta(days=3)).date()
        elif date_filter_text == "Last 7 Days":
            date_cutoff = (datetime.now() - timedelta(days=7)).date()
        elif date_filter_text == "Last 30 Days":
            date_cutoff = (datetime.now() - timedelta(days=30)).date()

        # Count visible items
        visible_count = 0

        for item_data in self.archive_items:
            # Check if query matches position, company, or tech stack
            text_match = (query in item_data['position'] or
                         query in item_data['company'] or
                         query in item_data['tech_stack'])

            # Check if rating meets minimum
            rating_match = item_data['match_rating'] >= min_rating

            # Check if job quality meets minimum
            quality_match = item_data['job_quality'] >= min_quality

            # Check if date matches filter
            if date_cutoff is None:
                date_match = True  # "Any day" - show all
            else:
                item_date = datetime.fromisoformat(item_data['date_created']).date()
                if date_filter_text == "Today":
                    date_match = item_date == date_cutoff
                else:
                    # "Last X Days" - show items from cutoff date onwards
                    date_match = item_date >= date_cutoff

            # Show item only if all conditions are met
            is_visible = text_match and rating_match and quality_match and date_match
            item_data['widget'].setVisible(is_visible)

            # Update counts
            if is_visible:
                visible_count += 1

        # Update title label with filtered count
        self.archive_title_label.setText(f"Archive ({visible_count} Results)")

    def create_archive_item(self, data):
        """Create a simplified archive item widget showing company, match rate, job quality, and applied date"""
        from Utility import restore_archive_data
        from Widgets import ActionBarButton
        
        job_data = data['Job']

        # Extract data
        company = job_data['Company Name']
        position = job_data['Position Title']
        date_applied = job_data.get('Date Applied', "N/A")
        expected_response = job_data.get('Expected Response Date', "N/A")
        match_rating = job_data.get('Match Rating', 0)
        job_quality = job_data.get('Job Quality', 5)

        try:
            match_rating = float(match_rating)
        except:
            match_rating = 5.0

        try:
            job_quality = float(job_quality)
        except:
            job_quality = 5.0

        # Main widget
        item_widget = QWidget()
        item_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: none;
                border-radius: 8px;
            }
        """)

        item_layout = QHBoxLayout(item_widget)
        item_layout.setSpacing(16)
        item_layout.setContentsMargins(20, 12, 20, 12)

        # Company name label
        company_label = QLabel(f"{position} at {company}")
        company_label.setStyleSheet("font-size: 13pt; font-weight: bold; color: #1a1a1a;")
        item_layout.addWidget(company_label)

        item_layout.addStretch()

        # Job Quality badge
        if job_quality is not None:
            # Determine color based on job quality
            if job_quality >= 8:
                quality_color = "#2e7d32"  # Dark green
                quality_bg = "#e8f5e9"     # Light green bg
            elif job_quality >= 5:
                quality_color = "#ef6c00"  # Dark orange
                quality_bg = "#fff3e0"     # Light orange bg
            else:
                quality_color = "#c62828"  # Dark red
                quality_bg = "#ffebee"     # Light red bg

            quality_label = QLabel(f"💎 {job_quality}/10")
            quality_label.setStyleSheet(f"""
                font-size: 9pt;
                color: {quality_color};
                font-weight: 600;
                background-color: {quality_bg};
                padding: 4px 10px;
                border-radius: 6px;
            """)
            item_layout.addWidget(quality_label)

        # Match rating badge
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
                font-size: 9pt;
                color: {rating_color};
                font-weight: 600;
                background-color: {rating_bg};
                padding: 4px 10px;
                border-radius: 6px;
            """)
            item_layout.addWidget(match_label)

        # Date range label (applied - expected response)
        date_range_text = f"{date_applied} - {expected_response}"
        date_label = QLabel(date_range_text)
        date_label.setStyleSheet("""
            font-size: 9pt;
            color: #757575;
            background-color: #f5f5f5;
            padding: 4px 10px;
            border-radius: 6px;
        """)
        item_layout.addWidget(date_label)

        # Restore button
        def on_restore_click(event):
            event.accept()
            self.restore_archive_item(data)

        restore_btn = ActionBarButton("↩️", "Restore", on_restore_click)
        item_layout.addWidget(restore_btn)

        # Delete button
        def on_delete_click(event):
            event.accept()
            self.delete_archive_item(data)

        delete_btn = ActionBarButton("🗑️", "Delete", on_delete_click,
                                     hover_color="#ffebee", hover_border="#f44336", pressed_color="#ffcdd2")
        item_layout.addWidget(delete_btn)

        return item_widget

    def restore_archive_item(self, data):
        """Restore an archived item back to the history section"""
        from Utility import restore_archive_data
        from PySide6.QtWidgets import QMessageBox

        file_name = f"{data['Meta']['File Name']}"

        # Show confirmation dialog
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Restore Archive")
        msg_box.setText(f"Restore '{file_name}' back to history?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)

        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            # Restore the JSON file
            restore_archive_data(file_name)

            # Refresh the archive page
            self.show_archive_page()

    def delete_archive_item(self, data):
        """Delete an archived item permanently"""
        from Utility import paths
        from PySide6.QtWidgets import QMessageBox
        import os

        file_name = f"{data['Meta']['File Name']}"

        # Show confirmation dialog
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Delete Archived Item")
        msg_box.setText(f"Are you sure you want to permanently delete this item?")
        msg_box.setInformativeText(f"{file_name}\n\nThis action cannot be undone.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            # Delete the JSON file from archive folder
            archived_path = paths['json_data'] / 'Archived'
            json_file_path = archived_path / f"{file_name}.json"
            if json_file_path.exists():
                os.remove(json_file_path)
                print(f"Deleted archived item: {file_name}")

            # Refresh the archive page
            self.show_archive_page()

    #endregion

    #region Statistics Page

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

    #endregion

    #region Settings Page
    
    def create_settings_page(self):
        """Create the settings page"""
        # Load config data
        self.config_data = get_config()

        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Settings")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Auto Archive Settings
        from Widgets import SettingsCheckbox

        self.auto_archive_checkbox = SettingsCheckbox(
            "Auto Archive Expired Applications",
            main_layout,
            is_checked=self.config_data['Settings']['Auto Archive Expired Applications'],
            on_change=self.save_settings
        )

        self.auto_archive_favorites_checkbox = SettingsCheckbox(
            "Auto Archive Expired Favorite Applications",
            main_layout,
            is_checked=self.config_data['Settings'].get('Auto Archive Expired Favorite Applications', False),
            on_change=self.save_settings,
            tooltip="When enabled, favorite applications will also be auto-archived after they expire"
        )

        self.show_ai_stream_checkbox = SettingsCheckbox(
            "Show AI Response Stream",
            main_layout,
            is_checked=self.config_data['Settings'].get('Show AI Response Stream', False),
            on_change=self.save_settings,
            tooltip="When enabled, a modal shows the AI's response streaming in live while generating a resume or checking a rating"
        )

        # GPT Model Setting
        model_layout = QVBoxLayout()
        model_layout.setSpacing(8)

        model_label = QLabel("GPT Model:")
        model_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #333;")
        model_layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.addItems(self.config_data['Resources']['Available Models'])
        current_model = self.config_data['Settings']['Current Model']
        self.model_combo.setCurrentText(current_model)
        self.model_combo.setMinimumHeight(40)
        self.model_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 11pt;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 10px;
            }
        """)
        self.model_combo.currentTextChanged.connect(self.save_settings)
        model_layout.addWidget(self.model_combo)

        main_layout.addLayout(model_layout)

        # Anthropic Thinking Settings
        anthropic_settings = self.config_data['Settings'].get('Anthropic', {})

        combo_style = """
            QComboBox {
                padding: 10px;
                font-size: 11pt;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 10px;
            }
        """

        thinking_layout = QVBoxLayout()
        thinking_layout.setSpacing(8)

        thinking_label = QLabel("Claude Thinking Type:")
        thinking_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #333;")
        thinking_layout.addWidget(thinking_label)

        self.thinking_type_combo = QComboBox()
        self.thinking_type_combo.addItems(["adaptive", "disabled"])
        self.thinking_type_combo.setCurrentText(anthropic_settings.get('Thinking Type', 'adaptive'))
        self.thinking_type_combo.setMinimumHeight(40)
        self.thinking_type_combo.setStyleSheet(combo_style)
        self.thinking_type_combo.currentTextChanged.connect(self.save_settings)
        thinking_layout.addWidget(self.thinking_type_combo)

        main_layout.addLayout(thinking_layout)

        # Effort Setting
        effort_layout = QVBoxLayout()
        effort_layout.setSpacing(8)

        effort_label = QLabel("Claude Thinking Effort:")
        effort_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #333;")
        effort_layout.addWidget(effort_label)

        self.effort_combo = QComboBox()
        self.effort_combo.addItems(["low", "medium", "high", "xhigh"])
        self.effort_combo.setCurrentText(anthropic_settings.get('Effort', 'medium'))
        self.effort_combo.setMinimumHeight(40)
        self.effort_combo.setStyleSheet(combo_style)
        self.effort_combo.currentTextChanged.connect(self.save_settings)
        effort_layout.addWidget(self.effort_combo)

        main_layout.addLayout(effort_layout)

        # Add stretch to push content to top
        main_layout.addStretch()

        # Add page to stacked widget
        self.stacked_widget.addWidget(page)

    def save_settings(self):
        """Save settings to Config.json using update_config"""
        # Update config data
        self.config_data['Settings']['Auto Archive Expired Applications'] = self.auto_archive_checkbox.isChecked()
        self.config_data['Settings']['Auto Archive Expired Favorite Applications'] = self.auto_archive_favorites_checkbox.isChecked()
        self.config_data['Settings']['Show AI Response Stream'] = self.show_ai_stream_checkbox.isChecked()
        self.config_data['Settings']['Current Model'] = self.model_combo.currentText()

        self.config_data['Settings'].setdefault('Anthropic', {})
        self.config_data['Settings']['Anthropic']['Thinking Type'] = self.thinking_type_combo.currentText()
        self.config_data['Settings']['Anthropic']['Effort'] = self.effort_combo.currentText()

        # Save to file using Utility function
        update_config(self.config_data)

        print(f"Settings saved: Auto Archive = {self.auto_archive_checkbox.isChecked()}, Auto Archive Favorites = {self.auto_archive_favorites_checkbox.isChecked()}, Show AI Stream = {self.show_ai_stream_checkbox.isChecked()}, Model = {self.model_combo.currentText()}, Thinking Type = {self.thinking_type_combo.currentText()}, Effort = {self.effort_combo.currentText()}")

    #endregion

    #endregion


    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResumeApp()
    window.show()
    sys.exit(app.exec())
