import asyncio
import json
from datetime import datetime
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox
from Agent import create_request
from Utility import (json_template, full_base_resume_text, resume_template, cover_letter_template,
                      paths, save_json_obj, expand_list_to_keys, write_to_docx, clear_temp,
                      save_document_temp, copy_temp_to_results, convert_temp_to_pdf,
                      get_templates, play_notification_sound, get_config)
from icecream import ic


class AIWorker(QThread):
    """Worker thread for async AI requests"""
    finished = Signal(str)  # Signal to emit the response
    error = Signal(str)     # Signal to emit errors
    chunk = Signal(str)     # Signal to emit streamed response chunks

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
            response = loop.run_until_complete(create_request(self.message, on_chunk=self.chunk.emit))

            # Emit success signal
            self.finished.emit(response)

            loop.close()
        except Exception as e:
            # Emit error signal
            self.error.emit(str(e))


class ResumePage(QWidget):
    """Resume / cover letter generation page."""

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        from Widgets import InputText, InputTextBox
        """Create the resume generation page"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Company Name Field
        self.company_name = InputText("Company Name (Optional):", main_layout, "Enter the company name here...")

        # Job Title field
        self.job_title = InputText("Job Title (Optional):", main_layout, "Enter the job title here...")

        # Job Description text box
        self.job_description = InputTextBox("Job Description:", main_layout, "Paste the entire job description here...")

        # Application Link field
        self.application_link = InputText("Application Link (Optional):", main_layout, "Paste the job posting URL here...")

        # Save Submission checkbox
        self.save_submission_checkbox = QCheckBox("Save Submission (Not Applying - Save for Reference Only)")
        self.save_submission_checkbox.setMinimumHeight(40)
        self.save_submission_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 11pt;
                color: #333;
                padding: 8px;
                background-color: #fff3e0;
                border: 2px solid #ff9800;
                border-radius: 8px;
                padding-left: 12px;
            }
            QCheckBox:hover {
                background-color: #ffe0b2;
                border: 2px solid #f57c00;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        self.save_submission_checkbox.setToolTip("Check this if you're NOT applying but want to save this job for reference only. Documents won't be generated.")
        main_layout.addWidget(self.save_submission_checkbox)

        # Generate / Check Rating buttons
        generate_row = QHBoxLayout()

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
        self.generate_button.clicked.connect(lambda: self.on_generate())
        generate_row.addWidget(self.generate_button)

        self.check_rating_button = QPushButton("Check Rating")
        self.check_rating_button.setMinimumHeight(50)
        self.check_rating_button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #1b2733;
            }
        """)
        self.check_rating_button.clicked.connect(self.on_check_rating)
        generate_row.addWidget(self.check_rating_button)

        main_layout.addLayout(generate_row)

    def show_stream_modal(self, title):
        """Show a non-blocking modal that displays streamed AI output as it's received"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 10pt;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(text_edit)

        self.stream_dialog = dialog
        self.stream_text_edit = text_edit
        dialog.show()

    def on_stream_chunk(self, text):
        """Append a streamed AI response chunk to the stream modal, if it's open"""
        if getattr(self, 'stream_text_edit', None) is None:
            return
        if getattr(self, 'stage_timeline', None) is not None and self.stage_timeline.current_stage < 2:
            self.stage_timeline.set_stage(2)  # Generating Response
        self.stream_text_edit.moveCursor(QTextCursor.End)
        self.stream_text_edit.insertPlainText(text)
        self.stream_text_edit.moveCursor(QTextCursor.End)

    def close_stream_modal(self):
        """Close the stream modal, if it's open"""
        if getattr(self, 'stream_dialog', None) is not None:
            self.stream_dialog.close()
            self.stream_dialog = None
            self.stream_text_edit = None

    #region Progress Modal (Generate Resume)

    def show_progress_modal(self, title, stages):
        """Show a non-blocking modal with a stage timeline and streamed AI output"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QLabel, QPushButton
        from Pages.Resume.StageTimeline import StageTimeline

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(560, 440)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        timeline = StageTimeline(stages)
        layout.addWidget(timeline)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 10pt;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(text_edit)

        status_label = QLabel("")
        status_label.setWordWrap(True)
        status_label.setVisible(False)
        layout.addWidget(status_label)

        close_button = QPushButton("Close")
        close_button.setMinimumHeight(40)
        close_button.setVisible(False)
        close_button.setStyleSheet("""
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
        close_button.clicked.connect(self.close_progress_modal)
        layout.addWidget(close_button)

        self.stream_dialog = dialog
        self.stream_text_edit = text_edit
        self.stage_timeline = timeline
        self.progress_status_label = status_label
        self.progress_close_button = close_button
        dialog.show()

    def finish_progress_modal(self, success, message):
        """Mark the progress modal's timeline as finished (success or error) and reveal the Close button"""
        if getattr(self, 'stream_dialog', None) is None or getattr(self, 'stage_timeline', None) is None:
            # No enhanced progress modal in use for this request - fall back to a plain close
            self.close_stream_modal()
            return

        if success:
            self.stage_timeline.complete()
            self.progress_status_label.setText(f"✅ {message}")
            self.progress_status_label.setStyleSheet("font-size: 11pt; font-weight: 600; color: #2e7d32;")
        else:
            self.progress_status_label.setText(f"❌ {message}")
            self.progress_status_label.setStyleSheet("font-size: 11pt; font-weight: 600; color: #c62828;")

        self.progress_status_label.setVisible(True)
        self.progress_close_button.setVisible(True)

    def close_progress_modal(self):
        """Close the progress modal (triggered by its Close button) and clear its state"""
        if getattr(self, 'stream_dialog', None) is not None:
            self.stream_dialog.close()
        self.stream_dialog = None
        self.stream_text_edit = None
        self.stage_timeline = None
        self.progress_status_label = None
        self.progress_close_button = None

    #endregion

    def start_ai_worker(self, message, on_finished, on_error, stream_title, stages=None):
        """Create and start an AIWorker, optionally showing a live-streaming modal.

        If `stages` is given, the modal shows a StageTimeline instead of the plain
        streaming view, and stays open with a Close button once the request finishes.
        """
        from Utility import get_config

        show_stream = get_config()['Settings'].get('Show AI Response Stream', False)
        if show_stream:
            if stages:
                self.show_progress_modal(stream_title, stages)
                self.stage_timeline.set_stage(0)  # Parsing Information
            else:
                self.show_stream_modal(stream_title)

        worker = AIWorker(message)
        if show_stream and stages:
            worker.started.connect(lambda: self.stage_timeline.set_stage(1))  # Thinking
        worker.chunk.connect(self.on_stream_chunk)
        worker.finished.connect(on_finished)
        worker.error.connect(on_error)
        worker.start()
        return worker

    def on_check_rating(self):
        """Handle the check rating button click"""

        from Utility import full_base_resume_text, match_rating_prompt, job_quality_prompt

        job_title = self.job_title.text()
        company_name = self.company_name.text()
        job_desc = self.job_description.toPlainText()

        template = {
            'Match Rating': 'Scale from 1-10',
            'Match Rating Description': '',
            'Job Quality': 'Scale from 1-10',
            'Job Quality Description': ''
        }

        message = f'Current Resumes : {full_base_resume_text}\n'
        message += f"Match Rating Prompt: {match_rating_prompt}\n"
        message += f"Job Quality Prompt: {job_quality_prompt}\n"
        message += f"Job Title: {job_title}\nCompany: {company_name}\nJob Description: {job_desc}\n"
        message += f"Respond in json format using this template: {json.dumps(template)}"

        self.check_rating_button.setEnabled(False)
        self.check_rating_button.setText("Checking...")

        self.rating_worker = self.start_ai_worker(
            message, self.on_rating_response, self.on_rating_error, "Checking Rating..."
        )

    def on_rating_response(self, response):
        """Handle the rating AI response by showing a modal with the result"""

        self.close_stream_modal()

        self.check_rating_button.setEnabled(True)
        self.check_rating_button.setText("Check Rating")

        data = json.loads(response)

        self.current_match_rating = data['Match Rating']
        self.current_match_rating_description = data['Match Rating Description']
        self.current_job_quality = data['Job Quality']
        self.current_job_quality_description = data['Job Quality Description']

        self.show_rating_modal(
            self.current_match_rating,
            self.current_match_rating_description,
            self.current_job_quality,
            self.current_job_quality_description
        )

    def on_rating_error(self, error_message):
        """Handle errors from the rating AI request"""
        self.close_stream_modal()
        self.check_rating_button.setEnabled(True)
        self.check_rating_button.setText("Check Rating")
        self.on_ai_error(error_message)

    def show_rating_modal(self, match_rating, match_rating_description, job_quality, job_quality_description):
        """Show a modal with the match rating and job quality, with options to close or generate the resume"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle("Rating")
        dialog.setMinimumWidth(420)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Rating Results")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title_label)

        def rating_color_for(value):
            try:
                value = float(value)
            except (TypeError, ValueError):
                return "#c62828"
            if value >= 8:
                return "#2e7d32"
            elif value >= 5:
                return "#f57c00"
            else:
                return "#c62828"

        match_rating_label = QLabel(f"⭐ Match Rating: {match_rating}/10")
        match_rating_label.setStyleSheet(f"font-size: 20pt; font-weight: bold; color: {rating_color_for(match_rating)};")
        layout.addWidget(match_rating_label)

        match_description_label = QLabel(match_rating_description)
        match_description_label.setWordWrap(True)
        match_description_label.setStyleSheet("font-size: 11pt; color: #333;")
        layout.addWidget(match_description_label)

        job_quality_label = QLabel(f"⭐ Job Quality: {job_quality}/10")
        job_quality_label.setStyleSheet(f"font-size: 20pt; font-weight: bold; color: {rating_color_for(job_quality)};")
        layout.addWidget(job_quality_label)

        quality_description_label = QLabel(job_quality_description)
        quality_description_label.setWordWrap(True)
        quality_description_label.setStyleSheet("font-size: 11pt; color: #333;")
        layout.addWidget(quality_description_label)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 10, 0, 0)

        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet("""
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
        close_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(close_btn)

        generate_btn = QPushButton("Generate Resume")
        generate_btn.setMinimumHeight(40)
        generate_btn.setStyleSheet("""
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
        generate_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(generate_btn)

        layout.addLayout(button_layout)

        if dialog.exec():
            self.on_generate(with_rating=False)

    def on_generate(self, with_rating = True):
        """Handle the generate button click"""
        job_title = self.job_title.text()
        company_name = self.company_name.text()
        job_desc = self.job_description.toPlainText()

        # Disable button while processing
        self.generate_button.setEnabled(False)
        self.generate_button.setText("Generating...")

        # Reload templates and prompts
        get_templates()
        from Utility import resume_prompt, json_template, full_base_resume_text, match_rating_prompt, job_quality_prompt

        current_date_time = datetime.now().strftime("%B %d, %Y %I:%M %p")


        # Build the AI prompt
        message = f"My resumes:\n{full_base_resume_text}\n"
        message += f"Company Name: {company_name}\n Job Title: {job_title}\n Job Description: {job_desc}\n"
        message += f"{resume_prompt}\n"

        if with_rating:
            message += f"Match Rating: {match_rating_prompt}\n"
            message += f"Job Quality: {job_quality_prompt}"
        else:
            json_template['Job']['Match Rating'] = self.current_match_rating
            json_template['Job']['Match Rating Description'] = self.current_match_rating_description
            json_template['Job']['Job Quality'] = self.current_job_quality
            json_template['Job']['Job Quality Description'] = self.current_job_quality_description

        message += f"Please respond in a parsable json format that looks like this: \n{json.dumps(json_template)}\n"
        message += f"Also make sure to fillout the cover page. The time this request was made is {current_date_time}"

        self.current_prompt = message
        # Store company name and save_submission flag for use in callback

        # Create and start worker thread
        self.worker = self.start_ai_worker(
            message, self.on_ai_response, self.on_ai_error, "Generating Resume...",
            stages=["Parsing Information", "Thinking", "Generating Response", "Writing to Documents"]
        )

    def on_ai_response(self, response):
        """Handle successful AI response"""
        try:
            from Utility import get_config

            config = get_config()

            data = json.loads(response)

            clear_temp()

            play_notification_sound()


            # Check if this is a "Save Submission" (not applying)
            application_link = self.application_link.text()
            save_submission = self.save_submission_checkbox.isChecked()

            if save_submission:
                # Only save JSON, skip document generation
                self.generate_button.setText("Saving Data...")
            else:
                # Normal flow with document generation
                self.generate_button.setText("Processing Documents...")

            if getattr(self, 'stage_timeline', None) is not None:
                self.stage_timeline.set_stage(3)  # Writing to Documents

            resume_data = expand_list_to_keys(data['Resume'], "")
            cover_letter_data = data['CoverLetter']

            resume_name = resume_data['File Name']
            cover_letter_name = cover_letter_data['File Name']
            #region Editing Meta Data

            current_date_time = datetime.now()

            data['Meta']['Resume Path'] = str(paths['results'] / f"{resume_name}.docx")
            data['Meta']['Cover Letter Path'] = str(paths['results'] / f"{cover_letter_name}.docx")
            data['Meta']['Model Used'] = config['Settings']['Current Model']
            data['Meta']['Date Created'] = current_date_time.isoformat()
            data['Meta']['Favorite'] = False

            #endregion

            #region Editing Job data

            data['Job']['Save Submission'] = save_submission
            data['Job']['Application Link'] = application_link

            #endregion

            # clear_temp()

            save_json_obj(expand_list_to_keys(data, ""), f"{data['Meta']['File Name']}")

            # Only generate documents if NOT a "Save Submission"
            if not save_submission:
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

            if save_submission:
                print("Job saved successfully (no documents generated - Save Submission mode)")
                self.finish_progress_modal(True, "Job saved successfully! No documents were generated (Save Submission mode).")
            else:
                print("Resume generated successfully!")
                self.finish_progress_modal(True, "Resume and cover letter generated successfully!")
        except Exception as e:
            import traceback
            ic(type(e).__name__, str(e), response, traceback.format_exc())
            self.on_ai_error(str(e))

    def on_ai_error(self, error_msg):
        """Handle AI request errors"""
        self.finish_progress_modal(False, error_msg)
        print(f"Error: {error_msg}")

        # Re-enable button
        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generate Resume")
