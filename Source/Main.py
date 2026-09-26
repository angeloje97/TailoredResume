import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QStackedWidget)
from Utility import paths, get_config, update_config
from Components.SideBarButton import SideBarButton
from Components.PageTitle import PageTitle
from Components.SettingsCheckbox import SettingsCheckbox
from Components.SettingsComboBox import SettingsComboBox


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
        """Create the archive page and add it to the stacked widget"""
        from Pages.Archive.Index import ArchivePage

        self.archive_page = ArchivePage(self.stacked_widget)
        self.stacked_widget.addWidget(self.archive_page)

    def show_archive_page(self):
        """Refresh and show the archive page"""
        self.archive_page.show_page()

    #endregion

    #region Statistics Page

    def create_statistics_page(self):
        """Create the statistics page"""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        main_layout.addWidget(PageTitle("Statistics"))

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
        main_layout.addWidget(PageTitle("Settings"))

        # Auto Archive Settings
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
        self.model_combo = SettingsComboBox(
            "GPT Model:", main_layout,
            self.config_data['Resources']['Available Models'],
            current=self.config_data['Settings']['Current Model'],
            on_change=self.save_settings
        )

        # Anthropic Thinking Settings
        anthropic_settings = self.config_data['Settings'].get('Anthropic', {})

        self.thinking_type_combo = SettingsComboBox(
            "Claude Thinking Type:", main_layout, ["adaptive", "disabled"],
            current=anthropic_settings.get('Thinking Type', 'adaptive'),
            on_change=self.save_settings
        )

        # Effort Setting
        self.effort_combo = SettingsComboBox(
            "Claude Thinking Effort:", main_layout, ["low", "medium", "high", "xhigh"],
            current=anthropic_settings.get('Effort', 'medium'),
            on_change=self.save_settings
        )

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
