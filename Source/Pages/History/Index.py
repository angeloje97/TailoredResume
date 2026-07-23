import sys
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from Utility import (paths, expand_list_to_keys, write_to_docx, clear_temp,
                      save_document_temp, copy_temp_to_results, convert_temp_to_pdf,
                      resume_template, cover_letter_template)
from Pages.History.HistoryItem import HistoryItem


class FilesPage(QWidget):
    """History page listing generated (or saved-submission) job applications."""

    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self._build_ui()

    def _build_ui(self):
        """Create the files/history page container"""
        page_layout = QVBoxLayout(self)
        page_layout.setSpacing(0)
        page_layout.setContentsMargins(20, 20, 20, 0)

        # Title
        from Utility import get_json_datas

        datas = get_json_datas()
        count = len(datas)

        # Filter datas where Date Created is today
        today = datetime.now().date()
        datas_today = [data for data in datas if datetime.fromisoformat(data['Meta']['Date Created']).date() == today]

        self.history_title_label = QLabel(f"History ({count} Results) ({len(datas_today)} Today)")
        self.history_title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        page_layout.addWidget(self.history_title_label)

        # Create filter bar using reusable component
        from Widgets import FilterBar
        filters = FilterBar(on_filter_changed=self.filter_history_items,
                           include_favorites=True, include_saved=True)
        page_layout.addLayout(filters['layout'])

        # Store references to filter widgets
        self.search_bar = filters['search_bar']
        self.min_rating_combo = filters['min_rating']
        self.min_quality_combo = filters['min_quality']
        self.date_filter_combo = filters['date_filter']
        self.favorite_filter_checkbox = filters['favorites']
        self.show_saved_checkbox = filters['saved']

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

        today = datetime.now().date()
        datas_today = [data for data in datas if datetime.fromisoformat(data['Meta']['Date Created']).date() == today]

        # Update title with current count
        self.history_title_label.setText(f"History ({len(datas)} Results) ({len(datas_today)} Today)")

        # Store history items with their data for filtering
        self.history_items = []
        self.history_widgets = []  # Track all widget instances for expansion management

        # Add history items
        for data in datas:
            job_data = data['Job']
            history_item = HistoryItem(data, self)
            self.files_layout.addWidget(history_item)

            # Store widget reference
            self.history_widgets.append(history_item)

            # Store item with its searchable data
            self.history_items.append({
                'widget': history_item,
                'position': job_data['Position Title'].lower(),
                'company': job_data['Company Name'].lower(),
                'tech_stack': ' '.join(job_data['Tech Stack']).lower(),
                'match_rating': float(job_data.get('Match Rating', 0)),
                'job_quality': float(job_data.get('Job Quality', 0)),
                'date_created': data['Meta']['Date Created'],
                'favorite': data['Meta'].get('Favorite', False),
                'save_submission': job_data.get('Save Submission', False)
            })

        # Add stretch to push content to top
        self.files_layout.addStretch()

        # Clear search bar and reset filters
        self.search_bar.clear()
        self.min_rating_combo.setCurrentIndex(0)
        self.min_quality_combo.setCurrentIndex(0)
        self.date_filter_combo.setCurrentIndex(0)
        self.favorite_filter_checkbox.setChecked(False)
        self.show_saved_checkbox.setChecked(False)

        # Switch to files page
        self.stacked_widget.setCurrentWidget(self)

    #region Filter History Item

    def filter_history_items(self):
        """Filter history items based on search query, minimum rating, minimum job quality, date range, and favorites"""
        from datetime import datetime, timedelta

        query = self.search_bar.text().lower()

        # Get minimum rating filter
        rating_text = self.min_rating_combo.currentText()
        if rating_text == "All Ratings":
            min_rating = 0
        else:
            # Extract number from "X+" format
            min_rating = int(rating_text.rstrip('+'))

        # Get minimum job quality filter
        quality_text = self.min_quality_combo.currentText()
        if quality_text == "All Quality":
            min_quality = 0
        else:
            # Extract number from "X+" format
            min_quality = int(quality_text.rstrip('+'))

        # Get date filter
        date_filter_text = self.date_filter_combo.currentText()
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

        # Get favorite filter
        favorites_only = self.favorite_filter_checkbox.isChecked()

        # Get show saved filter
        show_saved_only = self.show_saved_checkbox.isChecked()

        # Count visible items
        visible_count = 0
        visible_today_count = 0
        today = datetime.now().date()

        for item_data in self.history_items:
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

            # Check if favorite filter matches
            if favorites_only:
                favorite_match = item_data['favorite']
            else:
                favorite_match = True  # Show all if not filtering by favorites

            # Check if save submission filter matches
            if show_saved_only:
                saved_match = item_data['save_submission']
            else:
                saved_match = True  # Show all if not filtering by saved submissions

            # Show item only if all conditions are met
            is_visible = text_match and rating_match and quality_match and date_match and favorite_match and saved_match
            item_data['widget'].setVisible(is_visible)

            # Update counts
            if is_visible:
                visible_count += 1
                # Check if item was created today
                item_date = datetime.fromisoformat(item_data['date_created']).date()
                if item_date == today:
                    visible_today_count += 1

        # Update title label with filtered counts
        self.history_title_label.setText(f"History ({visible_count} Results) ({visible_today_count} Today)")

    #endregion

    def collapse_all_history_items(self, except_widget=None):
        """Collapse all history items except the specified one"""
        for widget in self.history_widgets:
            if widget != except_widget and hasattr(widget, 'is_expanded'):
                widget.is_expanded = False
                if hasattr(widget, 'details_widget'):
                    widget.details_widget.setVisible(False)

    #region Archive History Item

    def archive_history_item(self, data):
        """Archive a history item by moving its JSON file to archive folder"""
        from Utility import archive_json_data
        from PySide6.QtWidgets import QMessageBox

        file_name = f"{data['Meta']['File Name']}"
        # Show confirmation dialog

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle("Archive History Item")
        msg_box.setText(f"Are you sure you want to archive this item?")
        msg_box.setInformativeText(f"{file_name}")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            # Archive the JSON file
            archive_json_data(file_name)

            # Refresh the history page
            self.show_files_page()

    #endregion

    #region Delete History Item

    def delete_history_item(self, data):
        """Delete a history item by removing its JSON file permanently"""
        from PySide6.QtWidgets import QMessageBox
        import os

        file_name = f"{data['Meta']['File Name']}"
        # Show confirmation dialog

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Delete History Item")
        msg_box.setText(f"Are you sure you want to permanently delete this item?")
        msg_box.setInformativeText(f"{file_name}\n\nThis action cannot be undone.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            # Delete the JSON file
            json_file_path = paths['json_data'] / f"{file_name}.json"
            if json_file_path.exists():
                os.remove(json_file_path)
                print(f"Deleted: {file_name}")

            # Refresh the history page
            self.show_files_page()

    #endregion

    def update_dates(self, data, item_widget):
        """Update the Date Applied and Expected Response Date for a history item"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
        from datetime import datetime, timedelta

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Dates")
        dialog.setMinimumWidth(450)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Update Application Dates")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title_label)

        # Current dates info
        current_date_applied = data['Job']['Date Applied']
        current_expected_response = data['Job']['Expected Response Date']
        info_label = QLabel(f"Current: {current_date_applied} → {current_expected_response}")
        info_label.setStyleSheet("font-size: 11pt; color: #666;")
        layout.addWidget(info_label)

        # Date Applied input section
        date_applied_label = QLabel("Date Applied (mm/dd/yy):")
        date_applied_label.setStyleSheet("font-size: 11pt; font-weight: bold; margin-top: 10px;")
        layout.addWidget(date_applied_label)

        date_applied_input = QLineEdit()
        date_applied_input.setPlaceholderText("e.g., 01/15/25")
        date_applied_input.setText(current_date_applied)
        date_applied_input.setMinimumHeight(40)
        date_applied_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 11pt;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        layout.addWidget(date_applied_input)

        # Quick select buttons for Date Applied
        quick_select_applied_layout = QHBoxLayout()
        quick_select_applied_layout.setSpacing(8)

        today_applied_btn = QPushButton("Today")
        today_applied_btn.setStyleSheet("""
            QPushButton {
                background-color: #e3f2fd;
                color: #1976d2;
                font-size: 10pt;
                font-weight: bold;
                border: 1px solid #2196F3;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #bbdefb;
            }
        """)
        today_applied_btn.clicked.connect(lambda: date_applied_input.setText(datetime.now().strftime("%m/%d/%y")))
        quick_select_applied_layout.addWidget(today_applied_btn)

        quick_select_applied_layout.addStretch()
        layout.addLayout(quick_select_applied_layout)

        # Expected Response Date input section
        expected_response_label = QLabel("Expected Response Date (mm/dd/yy):")
        expected_response_label.setStyleSheet("font-size: 11pt; font-weight: bold; margin-top: 10px;")
        layout.addWidget(expected_response_label)

        expected_response_input = QLineEdit()
        expected_response_input.setPlaceholderText("e.g., 01/29/25")
        expected_response_input.setText(current_expected_response)
        expected_response_input.setMinimumHeight(40)
        expected_response_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 11pt;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        layout.addWidget(expected_response_input)

        # Quick select buttons for Expected Response Date
        quick_select_response_layout = QHBoxLayout()
        quick_select_response_layout.setSpacing(8)

        def set_response_date(days):
            try:
                applied_date = datetime.strptime(date_applied_input.text(), "%m/%d/%y")
                response_date = applied_date + timedelta(days=days)
                expected_response_input.setText(response_date.strftime("%m/%d/%y"))
            except:
                # If date applied is invalid, calculate from today
                response_date = datetime.now() + timedelta(days=days)
                expected_response_input.setText(response_date.strftime("%m/%d/%y"))

        plus_7_btn = QPushButton("+7 Days")
        plus_7_btn.setStyleSheet("""
            QPushButton {
                background-color: #e8f5e9;
                color: #2e7d32;
                font-size: 10pt;
                font-weight: bold;
                border: 1px solid #4CAF50;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #c8e6c9;
            }
        """)
        plus_7_btn.clicked.connect(lambda: set_response_date(7))
        quick_select_response_layout.addWidget(plus_7_btn)

        plus_14_btn = QPushButton("+14 Days")
        plus_14_btn.setStyleSheet("""
            QPushButton {
                background-color: #e8f5e9;
                color: #2e7d32;
                font-size: 10pt;
                font-weight: bold;
                border: 1px solid #4CAF50;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #c8e6c9;
            }
        """)
        plus_14_btn.clicked.connect(lambda: set_response_date(14))
        quick_select_response_layout.addWidget(plus_14_btn)

        plus_30_btn = QPushButton("+30 Days")
        plus_30_btn.setStyleSheet("""
            QPushButton {
                background-color: #e8f5e9;
                color: #2e7d32;
                font-size: 10pt;
                font-weight: bold;
                border: 1px solid #4CAF50;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #c8e6c9;
            }
        """)
        plus_30_btn.clicked.connect(lambda: set_response_date(30))
        quick_select_response_layout.addWidget(plus_30_btn)

        quick_select_response_layout.addStretch()
        layout.addLayout(quick_select_response_layout)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 10, 0, 0)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333;
                font-size: 11pt;
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Update")
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 11pt;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        save_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        # Show dialog and handle result
        if dialog.exec():
            new_date_applied = date_applied_input.text().strip()
            new_expected_response = expected_response_input.text().strip()

            # Validate date formats
            try:
                datetime.strptime(new_date_applied, "%m/%d/%y")
                datetime.strptime(new_expected_response, "%m/%d/%y")

                # Update the data
                data['Job']['Date Applied'] = new_date_applied
                data['Job']['Expected Response Date'] = new_expected_response

                # Save the updated JSON
                from Utility import save_json_obj, expand_list_to_keys
                save_json_obj(expand_list_to_keys(data, ""), f"{data['Meta']['File Name']}")

                print(f"Updated dates for: {data['Job']['Position Title']} at {data['Job']['Company Name']}")
                print(f"  Date Applied: {new_date_applied}")
                print(f"  Expected Response: {new_expected_response}")

                # Refresh the history page to show updated dates
                self.show_files_page()

            except ValueError:
                from PySide6.QtWidgets import QMessageBox
                error_box = QMessageBox()
                error_box.setIcon(QMessageBox.Icon.Warning)
                error_box.setWindowTitle("Invalid Date Format")
                error_box.setText("Please enter valid dates in mm/dd/yy format for both fields.")
                error_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                error_box.exec()

    def open_result_folder(self, data):
        """Open the Results folder containing the resume and cover letter files"""
        import os
        import subprocess

        # Open the Results folder in file explorer
        results_path = str(paths['results'])

        if os.name == 'nt':  # Windows
            os.startfile(results_path)
        elif os.name == 'posix':  # macOS and Linux
            subprocess.run(['open', results_path] if sys.platform == 'darwin' else ['xdg-open', results_path])

    def generate_documents(self, data):
        """Generate documents (resume and cover letter) for a history item"""
        clear_temp()
        resume_data = expand_list_to_keys(data['Resume'], "")
        cover_letter_data = data['CoverLetter']

        resume_doc = write_to_docx(resume_template, resume_data)
        cover_letter_doc = write_to_docx(cover_letter_template, cover_letter_data)

        save_document_temp(resume_doc, resume_data['File Name'])
        save_document_temp(cover_letter_doc, cover_letter_data['File Name'])

        convert_temp_to_pdf()

        copy_temp_to_results()

