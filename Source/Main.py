import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QTextEdit,
                               QPushButton, QStackedWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


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
        title_label = QLabel("Base Resumes")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Placeholder content
        info_label = QLabel("This page will show the list of human created resumes.")
        info_label.setStyleSheet("font-size: 12pt; color: #666;")
        main_layout.addWidget(info_label)

        # Add stretch to push content to top
        main_layout.addStretch()

        # Add page to stacked widget
        self.stacked_widget.addWidget(page)

    def on_generate(self):
        """Handle the generate button click"""
        job_title = self.job_title.text()
        company_name = self.company_name.text()
        job_desc = self.job_description.toPlainText()

        print("=" * 50)
        print("GENERATE BUTTON CLICKED")
        print("=" * 50)
        print(f"Company Name: {company_name}")
        print(f"Job Title: {job_title}")
        print(f"Job Description Length: {len(job_desc)} characters")
        print(f"\nJob Description Preview:\n{job_desc[:200]}...")
        print("=" * 50)

        # TODO: Add your resume generation logic here


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResumeApp()
    window.show()
    sys.exit(app.exec())
