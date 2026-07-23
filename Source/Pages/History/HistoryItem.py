from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton


class HistoryItem(QWidget):
    """A single expandable job-application entry on the History page."""

    def __init__(self, data, page):
        super().__init__()
        self.data = data
        self.page = page
        self.is_expanded = False
        self._build_ui()

    def _build_ui(self):
        data = self.data
        job_data = data['Job']
        #region Main History Item
        position = job_data['Position Title']
        company = job_data['Company Name']
        start_date = job_data['Date Applied']
        end_date = job_data['Expected Response Date']
        tags = job_data.get('Tech Stack', None)
        salary = job_data.get('Salary', None)
        match_rating = float(job_data.get('Match Rating', 0))
        job_quality = float(job_data.get('Job Quality', 5))
        save_submission = job_data.get('Save Submission', False)
        application_link = job_data.get('Application Link', '')

        current_date = datetime.now()

        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
            }
            QWidget:hover {
                background-color: #fafafa;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        item_layout = QVBoxLayout(self)
        item_layout.setSpacing(12)
        item_layout.setContentsMargins(20, 16, 20, 16)

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
                font-size: 10pt;
                color: {quality_color};
                font-weight: 600;
                background-color: {quality_bg};
                padding: 4px 10px;
                border-radius: 6px;
            """)
            header_layout.addWidget(quality_label)

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

        # Save Submission badge (always created, visibility controlled)
        save_submission_badge = QLabel("📋 Saved")
        save_submission_badge.setStyleSheet("""
            font-size: 9pt;
            color: #ff6f00;
            font-weight: 600;
            background-color: #fff3e0;
            padding: 4px 10px;
            border-radius: 6px;
            border: 2px solid #ff9800;
        """)
        save_submission_badge.setToolTip("This is a saved submission (not applying)")
        save_submission_badge.setVisible(save_submission)
        header_layout.addWidget(save_submission_badge)

        # Archive button with file-box icon
        archive_btn = QPushButton("📦")
        archive_btn.setFixedSize(36, 36)
        archive_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        archive_btn.setToolTip("Archive this application")
        archive_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16pt;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
                border: 2px solid #1976d2;
            }
            QPushButton:pressed {
                background-color: #bbdefb;
            }
        """)

        # Prevent click from expanding the item
        def on_archive_click(event):
            event.accept()
            self.page.archive_history_item(data)

        archive_btn.mousePressEvent = on_archive_click
        header_layout.addWidget(archive_btn)

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
        responsibilities = "\n- ".join(job_data['Responsibilities'])
        company_size = job_data['Company Size']
        job_quality_description = job_data.get('Job Quality Description', "NA")
        motive = job_data.get("Motive", "NA")
        match_rating_reasoning = job_data.get("Match Rating Description", "NA")

        details_widget = QWidget()
        details_widget.setVisible(False)
        details_layout = QVBoxLayout(details_widget)
        details_layout.setSpacing(10)
        details_layout.setContentsMargins(0, 10, 0, 0)

        # Prevent mouse events from propagating to parent
        details_widget.mousePressEvent = lambda e: e.accept()

        # Action bar at the top of expanded section
        from Widgets import ActionBarButton, ToggleActionBarButton

        action_bar = QWidget()
        action_bar.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        action_bar_layout = QHBoxLayout(action_bar)
        action_bar_layout.setContentsMargins(10, 5, 10, 5)
        action_bar_layout.setSpacing(8)

        # Add stretch to push icons to the right
        action_bar_layout.addStretch()

        # Update Dates button

        def on_calendar_click(event):
            event.accept()
            self.page.update_dates(data, self)

        calendar_btn = ActionBarButton("📅", "Update Dates", on_calendar_click,
                                       hover_color="#e8f5e9", hover_border="#4CAF50", pressed_color="#c8e6c9")
        action_bar_layout.addWidget(calendar_btn)

        # Application Link button (if provided)
        if application_link:
            def on_link_click(event):
                event.accept()
                import webbrowser
                webbrowser.open(application_link)

            link_btn = ActionBarButton("🔗", "Open Application Link", on_link_click)
            action_bar_layout.addWidget(link_btn)

        # Folder icon button (open folder)
        def on_folder_click(event):
            event.accept()
            self.page.open_result_folder(data)

        folder_btn = ActionBarButton("📁", "Open in folder", on_folder_click,
                                     hover_color="#fff3e0", hover_border="#ff9800", pressed_color="#ffe0b2")
        action_bar_layout.addWidget(folder_btn)

        # Generate Documents icon button
        def on_generate_docs_click(event):
            event.accept()
            self.page.generate_documents(data)

        generate_docs_btn = ActionBarButton("📝", "Generate Documents", on_generate_docs_click)
        action_bar_layout.addWidget(generate_docs_btn)

        # Favorite icon button
        is_favorite = data['Meta'].get('Favorite', False)
        favorite_btn, update_favorite_style = ToggleActionBarButton("⭐", "Favorite", is_favorite)

        def on_favorite_click(event):
            event.accept()
            # Toggle favorite status
            current_favorite = data['Meta'].get('Favorite', False)
            data['Meta']['Favorite'] = not current_favorite

            # Update the JSON file
            from Utility import save_json_obj, expand_list_to_keys
            save_json_obj(expand_list_to_keys(data, ""), f"{data['Meta']['File Name']}")

            # Update button style
            update_favorite_style(data['Meta']['Favorite'])

            # Update the history item data for filtering
            for item_data in self.page.history_items:
                if item_data['widget'] == self:
                    item_data['favorite'] = data['Meta']['Favorite']
                    break

            print(f"{'Favorited' if data['Meta']['Favorite'] else 'Unfavorited'}: {data['Job']['Position Title']} at {data['Job']['Company Name']}")

        favorite_btn.mousePressEvent = on_favorite_click
        action_bar_layout.addWidget(favorite_btn)

        # Save Submission toggle button
        is_save_submission = data['Job'].get('Save Submission', False)
        save_submission_btn, update_save_submission_style = ToggleActionBarButton(
            "📋", "Toggle Save Submission (Not Applying)", is_save_submission,
            active_bg="#ff9800", active_border="#ff9800",
            active_hover="#f57c00", active_pressed="#ef6c00",
            inactive_hover="#fff3e0", inactive_border="#ff9800", inactive_pressed="#ffe0b2"
        )

        def on_save_submission_click(event):
            event.accept()
            # Toggle save submission status
            current_save_submission = data['Job'].get('Save Submission', False)
            data['Job']['Save Submission'] = not current_save_submission

            # Update the JSON file
            from Utility import save_json_obj, expand_list_to_keys
            save_json_obj(expand_list_to_keys(data, ""), f"{data['Meta']['File Name']}")

            # Update button style
            update_save_submission_style(data['Job']['Save Submission'])

            # Update badge visibility in header
            save_submission_badge.setVisible(data['Job']['Save Submission'])

            print(f"{'Save Submission enabled' if data['Job']['Save Submission'] else 'Save Submission disabled'}: {data['Job']['Position Title']} at {data['Job']['Company Name']}")

        save_submission_btn.mousePressEvent = on_save_submission_click
        action_bar_layout.addWidget(save_submission_btn)

        # Delete icon button
        def on_delete_click(event):
            event.accept()
            self.page.delete_history_item(data)

        delete_btn = ActionBarButton("🗑️", "Delete", on_delete_click,
                                     hover_color="#ffebee", hover_border="#f44336", pressed_color="#ffcdd2")
        action_bar_layout.addWidget(delete_btn)

        details_layout.addWidget(action_bar)

        #region Details

        from Widgets import LabelDescription

        # Job Description

        LabelDescription("Description:", description, details_layout)

        # Match Rating Description

        LabelDescription("Match Rating Descripton:", match_rating_reasoning, details_layout)

        # Responsibilities

        LabelDescription("Responsibilities:", responsibilities, details_layout)

        # Company Size (horizontal layout)

        LabelDescription("Company Size:", company_size, details_layout, True)

        # Job Quality Description

        LabelDescription("Job Quality Description:", job_quality_description, details_layout)

        # Motive

        LabelDescription("Why Work Here:", motive, details_layout)

        item_layout.addWidget(details_widget)

        #endregion

        # Store reference to details widget for toggling
        self.details_widget = details_widget

        # Add click event to toggle expansion
        def toggle_expand(event):
            # Collapse all other items first
            self.page.collapse_all_history_items(except_widget=self)

            # Toggle this item
            self.is_expanded = not self.is_expanded
            details_widget.setVisible(self.is_expanded)

        self.mousePressEvent = toggle_expand

        #endregion
