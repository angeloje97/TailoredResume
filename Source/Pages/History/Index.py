import sys
from datetime import datetime
from PySide6.QtWidgets import QLabel, QMessageBox
from Utility import (paths, expand_list_to_keys, write_to_docx, clear_temp,
                      save_document_temp, copy_temp_to_results, convert_temp_to_pdf,
                      resume_template, cover_letter_template)
from Pages.History.HistoryItem import HistoryItem
from Components.PagedListPage import PagedListPage
from Components.ConfirmDialog import ConfirmDialog
from Components.StyledDialog import StyledDialog
from Components.Button import Button
from Components.ChipButton import ChipButton
from Components.StyledLineEdit import StyledLineEdit


class FilesPage(PagedListPage):
    """History page listing generated (or saved-submission) job applications."""

    def __init__(self, stacked_widget):
        super().__init__(stacked_widget, "History", include_favorites=True, include_saved=True,
                         list_spacing=15, list_margins=(0, 0, 20, 20))

    def load_datas(self):
        from Utility import get_json_datas
        return get_json_datas()

    def create_item(self, data):
        return HistoryItem(data, self)

    def title_text(self):
        today = datetime.now().date()
        today_count = sum(1 for entry in self.filtered
                          if datetime.fromisoformat(entry['date_created']).date() == today)
        return f"History ({len(self.filtered)} Results) ({today_count} Today)"

    def show_files_page(self):
        """Refresh and show the files page"""
        self.show_page()

    def collapse_all_history_items(self, except_widget=None):
        """Collapse all history items on the current page except the specified one"""
        for widget in self.item_widgets:
            if widget != except_widget and hasattr(widget, 'is_expanded'):
                widget.is_expanded = False
                if hasattr(widget, 'details_widget'):
                    widget.details_widget.setVisible(False)

    #region Archive History Item

    def archive_history_item(self, data):
        """Archive a history item by moving its JSON file to archive folder"""
        from Utility import archive_json_data

        file_name = f"{data['Meta']['File Name']}"

        if ConfirmDialog("Archive History Item", "Are you sure you want to archive this item?",
                         file_name, icon=QMessageBox.Icon.Question):
            # Archive the JSON file
            archive_json_data(file_name)

            # Refresh the history page
            self.reload()

    #endregion

    #region Delete History Item

    def delete_history_item(self, data):
        """Delete a history item by removing its JSON file permanently"""
        import os

        file_name = f"{data['Meta']['File Name']}"

        if ConfirmDialog("Delete History Item", "Are you sure you want to permanently delete this item?",
                         f"{file_name}\n\nThis action cannot be undone.", icon=QMessageBox.Icon.Warning):
            # Delete the JSON file
            json_file_path = paths['json_data'] / f"{file_name}.json"
            if json_file_path.exists():
                os.remove(json_file_path)
                print(f"Deleted: {file_name}")

            # Refresh the history page
            self.reload()

    #endregion

    def update_dates(self, data, item_widget):
        """Update the Date Applied and Expected Response Date for a history item"""
        from PySide6.QtWidgets import QHBoxLayout
        from datetime import timedelta

        dialog = StyledDialog(self, "Update Dates", heading="Update Application Dates", min_width=450)
        layout = dialog.body

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

        date_applied_input = StyledLineEdit("e.g., 01/15/25", current_date_applied)
        layout.addWidget(date_applied_input)

        # Quick select buttons for Date Applied
        quick_select_applied_layout = QHBoxLayout()
        quick_select_applied_layout.setSpacing(8)

        quick_select_applied_layout.addWidget(ChipButton(
            "Today", lambda: date_applied_input.setText(datetime.now().strftime("%m/%d/%y"))))

        quick_select_applied_layout.addStretch()
        layout.addLayout(quick_select_applied_layout)

        # Expected Response Date input section
        expected_response_label = QLabel("Expected Response Date (mm/dd/yy):")
        expected_response_label.setStyleSheet("font-size: 11pt; font-weight: bold; margin-top: 10px;")
        layout.addWidget(expected_response_label)

        expected_response_input = StyledLineEdit("e.g., 01/29/25", current_expected_response)
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

        for days in (7, 14, 30):
            quick_select_response_layout.addWidget(ChipButton(
                f"+{days} Days", lambda _=False, d=days: set_response_date(d), variant="green"))

        quick_select_response_layout.addStretch()
        layout.addLayout(quick_select_response_layout)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 10, 0, 0)

        button_layout.addWidget(Button("Cancel", dialog.reject, variant="secondary"))
        button_layout.addWidget(Button("Update", dialog.accept))

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
                self.reload()

            except ValueError:
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

