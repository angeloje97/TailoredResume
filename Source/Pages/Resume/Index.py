import asyncio
import json
import time
from datetime import datetime
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from Agent import create_request
from Components.AccentCheckbox import AccentCheckbox
from Components.Button import Button
from Components.StyledDialog import StyledDialog
from Components.StreamTextView import StreamTextView
from Components.ElapsedTimeLabel import ElapsedTimeLabel
from Components.AsyncLoader import AsyncLoader
from Components.WorkArrangementBadge import WorkArrangementBadge, normalize_work_arrangement
from Utility import (json_template, full_base_resume_text, paths, save_json_obj, expand_list_to_keys,
                      build_documents, get_templates, play_notification_sound, get_config, sanitize_file_name)
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
        from Components.InputText import InputText
        from Components.InputTextBox import InputTextBox
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
        self.save_submission_checkbox = AccentCheckbox(
            "Save Submission (Not Applying - Save for Reference Only)",
            hover_border="#f57c00", hover_background="#ffe0b2",
            background="#fff3e0", border="#ff9800", font_size=11, padding=8,
            tooltip="Check this if you're NOT applying but want to save this job for reference only. Documents won't be generated."
        )
        main_layout.addWidget(self.save_submission_checkbox)

        # Generate / Check Rating buttons
        generate_row = QHBoxLayout()

        self.generate_button = Button("Generate", lambda: self.on_generate(), size="large")
        generate_row.addWidget(self.generate_button)

        self.check_rating_button = Button("Check Rating", self.on_check_rating, variant="dark", size="large")
        generate_row.addWidget(self.check_rating_button)

        main_layout.addLayout(generate_row)

    def show_stream_modal(self, title, started_at=None):
        """Show a non-blocking modal that displays streamed AI output as it's received"""
        dialog = StyledDialog(self, title, min_size=(500, 400), margin=15, spacing=None)

        elapsed_label = ElapsedTimeLabel()
        elapsed_label.start(started_at)
        dialog.body.addWidget(elapsed_label)

        text_edit = StreamTextView()
        dialog.body.addWidget(text_edit)

        self.stream_dialog = dialog
        self.stream_text_edit = text_edit
        self.stream_elapsed_label = elapsed_label
        dialog.show()

    def on_stream_chunk(self, text):
        """Append a streamed AI response chunk to the stream modal, if it's open"""
        if getattr(self, 'stream_text_edit', None) is None:
            return
        if getattr(self, 'stage_timeline', None) is not None and self.stage_timeline.current_stage < 2:
            self.stage_timeline.set_stage(2)  # Generating Response
        self.stream_text_edit.append_chunk(text)

    def close_stream_modal(self):
        """Close the stream modal, if it's open"""
        if getattr(self, 'stream_dialog', None) is not None:
            self.stream_dialog.close()
            self.stream_dialog = None
            self.stream_text_edit = None
            self.stream_elapsed_label = None

    #region Progress Modal (Generate Resume)

    def show_progress_modal(self, title, stages, started_at=None):
        """Show a non-blocking modal with a stage timeline and streamed AI output"""
        from PySide6.QtWidgets import QLabel
        from Pages.Resume.StageTimeline import StageTimeline

        dialog = StyledDialog(self, title, min_size=(560, 440))
        layout = dialog.body

        timeline = StageTimeline(stages)
        layout.addWidget(timeline)

        elapsed_label = ElapsedTimeLabel()
        elapsed_label.start(started_at)
        layout.addWidget(elapsed_label)

        text_edit = StreamTextView()
        layout.addWidget(text_edit)

        status_label = QLabel("")
        status_label.setWordWrap(True)
        status_label.setVisible(False)
        layout.addWidget(status_label)

        close_button = Button("Close", self.close_progress_modal)
        close_button.setVisible(False)
        layout.addWidget(close_button)

        self.stream_dialog = dialog
        self.stream_text_edit = text_edit
        self.stage_timeline = timeline
        self.progress_status_label = status_label
        self.progress_close_button = close_button
        self.stream_elapsed_label = elapsed_label
        dialog.show()

    def finish_progress_modal(self, success, message):
        """Mark the progress modal's timeline as finished (success or error) and reveal the Close button"""
        if getattr(self, 'stream_dialog', None) is None or getattr(self, 'stage_timeline', None) is None:
            # No enhanced progress modal in use for this request - fall back to a plain close
            self.close_stream_modal()
            return

        self.stream_elapsed_label.stop("Finished in" if success else "Failed after")

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
        self.stream_elapsed_label = None

    #endregion

    def start_ai_worker(self, message, on_finished, on_error, stream_title, stages=None):
        """Create and start an AIWorker, optionally showing a live-streaming modal.

        If `stages` is given, the modal shows a StageTimeline instead of the plain
        streaming view, and stays open with a Close button once the request finishes.
        """
        from Utility import get_config

        started_at = time.monotonic()

        show_stream = get_config()['Settings'].get('Show AI Response Stream', False)
        if show_stream:
            if stages:
                self.show_progress_modal(stream_title, stages, started_at)
                self.stage_timeline.set_stage(0)  # Parsing Information
            else:
                self.show_stream_modal(stream_title, started_at)

        worker = AIWorker(message)
        worker.started_at = started_at  # So handlers can report total time taken
        if show_stream and stages:
            worker.started.connect(lambda: self.stage_timeline.set_stage(1))  # Thinking
        worker.chunk.connect(self.on_stream_chunk)
        worker.finished.connect(on_finished)
        worker.error.connect(on_error)
        worker.start()
        return worker

    def on_check_rating(self):
        """Handle the check rating button click"""

        # Reload prompts so edits to Resources/*.md apply without restarting
        get_templates()
        from Utility import full_base_resume_text, match_rating_prompt, job_quality_prompt, json_template

        job_title = self.job_title.text()
        company_name = self.company_name.text()
        job_desc = self.job_description.toPlainText()

        template = {
            'Match Rating': 'Scale from 1-10',
            'Match Rating Description': '',
            'Job Quality': 'Scale from 1-10',
            'Job Quality Description': '',
            'Work Arrangement': json_template['Job']['Work Arrangement']
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
        self.current_work_arrangement = normalize_work_arrangement(data.get('Work Arrangement'))

        self.show_rating_modal(
            self.current_match_rating,
            self.current_match_rating_description,
            self.current_job_quality,
            self.current_job_quality_description,
            self.current_work_arrangement,
            elapsed_seconds=time.monotonic() - self.rating_worker.started_at
        )

    def on_rating_error(self, error_message):
        """Handle errors from the rating AI request"""
        self.close_stream_modal()
        self.check_rating_button.setEnabled(True)
        self.check_rating_button.setText("Check Rating")
        self.on_ai_error(error_message)

    def show_rating_modal(self, match_rating, match_rating_description, job_quality, job_quality_description,
                          work_arrangement="Unknown", elapsed_seconds=None):
        """Show a modal with the match rating and job quality, with options to close or generate the resume"""
        from PySide6.QtWidgets import QLabel
        from Components.RatingBadge import rating_colors
        from Components.RatingBreakdown import RatingBreakdown
        from Components.ScrollList import ScrollList

        dialog = StyledDialog(self, "Rating", heading="Rating Results", min_width=560)
        layout = dialog.body

        if elapsed_seconds is not None:
            layout.addWidget(ElapsedTimeLabel(elapsed_seconds, prefix="Took"))

        # Long descriptions scroll inside this area so the buttons below stay reachable
        scroll = ScrollList(spacing=12, margins=(0, 0, 12, 0), align_top=True)
        scroll.viewport().setStyleSheet("background-color: white;")
        layout.addWidget(scroll, 1)

        for title, value, description in (("Match Rating", match_rating, match_rating_description),
                                          ("Job Quality", job_quality, job_quality_description)):
            rating_label = QLabel(f"⭐ {title}: {value}/10")
            rating_label.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {rating_colors(value)[0]};"
                                       f" padding-top: 6px;")
            scroll.add(rating_label)
            scroll.add(RatingBreakdown(description))

        # Cap the dialog at 80% of the screen height; the scroll area absorbs the rest
        available = self.screen().availableGeometry()
        dialog.setMaximumHeight(int(available.height() * 0.9))
        dialog.resize(640, int(available.height() * 0.8))

        work_arrangement_row = QHBoxLayout()
        work_arrangement_row.addWidget(WorkArrangementBadge(work_arrangement, font_size=11))
        work_arrangement_row.addStretch()
        layout.addLayout(work_arrangement_row)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 10, 0, 0)

        button_layout.addWidget(Button("Close", dialog.reject, variant="secondary"))
        button_layout.addWidget(Button("Generate Resume", dialog.accept))

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
            json_template['Job']['Work Arrangement'] = self.current_work_arrangement

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

            # AI-written names can contain characters Windows can't save (e.g. "React / Next.js")
            for section in ('Meta', 'Resume', 'CoverLetter'):
                data[section]['File Name'] = sanitize_file_name(data[section]['File Name'])

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
            data['Job']['Work Arrangement'] = normalize_work_arrangement(data['Job'].get('Work Arrangement'))

            #endregion

            # clear_temp()

            save_json_obj(expand_list_to_keys(data, ""), f"{data['Meta']['File Name']}")

            if save_submission:
                # Only save JSON, skip document generation
                self.generate_button.setEnabled(True)
                self.generate_button.setText("Generate Resume")
                print("Job saved successfully (no documents generated - Save Submission mode)")
                self.finish_progress_modal(True, "Job saved successfully! No documents were generated (Save Submission mode).")
            else:
                # Filling templates + PDF conversion (Word) takes seconds, so do it off the GUI thread
                self.documents_worker = AsyncLoader(lambda: build_documents(resume_data, cover_letter_data), self)
                self.documents_worker.loaded.connect(self.on_documents_built)
                self.documents_worker.failed.connect(self.on_ai_error)
                self.documents_worker.start()
        except Exception as e:
            import traceback
            ic(type(e).__name__, str(e), response, traceback.format_exc())
            self.on_ai_error(str(e))

    def on_documents_built(self, _):
        """Handle the background document build finishing successfully"""
        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generate Resume")
        print("Resume generated successfully!")
        self.finish_progress_modal(True, "Resume and cover letter generated successfully!")

    def on_ai_error(self, error_msg):
        """Handle AI request errors"""
        self.finish_progress_modal(False, error_msg)
        print(f"Error: {error_msg}")

        # Re-enable button
        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generate Resume")
