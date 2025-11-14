import sys
import asyncio
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QTextEdit,
                               QPushButton, QStackedWidget)
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
        self.setGeometry(100, 100, 1000, 600)

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
        self.files_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        sidebar_layout.addWidget(self.files_btn)

        # Add stretch to push buttons to top
        sidebar_layout.addStretch()

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

    def create_files_page(self):
        """Create the files/history page"""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("History")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Placeholder content
        info_label = QLabel("This page will show all the generated resumes.")
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
            
            resume_data = expand_list_to_keys(data['Resume'], "")
            cover_letter_data = data['CoverLetter']

            resume_name = resume_data['File Name']
            cover_letter_name = cover_letter_data['File Name']
            #region Editing Meta Data

            data['Meta']['Resume Path'] = str(paths['results'] / f"{resume_name}.docx")
            data['Meta']['Cover Letter Path'] = str(paths['results'] / f"{cover_letter_name}.docx")
            data['Meta']['Model Used'] = model
            #endregion

            # clear_temp()

            save_json_obj(expand_list_to_keys(data, ""), f"{meta['File Name']} Data")
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
