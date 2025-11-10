# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python desktop application for tailoring resumes using AI. It features a PySide6 GUI that collects job descriptions and uses OpenAI's API to generate customized resumes from base templates stored in `BaseResumes/`.

## Project Structure

```
.
├── BaseResumes/     # Source resume templates (.docx files)
│   └── Resume2025_*.docx  # Latest resume versions (D, M, 3 variants)
├── Resources/       # Supporting resources
│   ├── Json Template.json   # Resume data structure template
│   └── Resume Template.docx # Base formatting template
├── Results/         # Generated tailored resumes (output directory)
├── Source/          # Python source code
│   ├── Main.py      # PySide6 GUI application (entry point)
│   ├── Utility.py   # Document processing utilities
│   └── Agent.py     # OpenAI API integration
├── .env             # Environment variables (API keys) - DO NOT COMMIT
├── requirements.txt # Python dependencies
├── install.bat      # Windows installation script
└── run.bat          # Windows run script
```

## Architecture

### Core Modules

**Main.py** - PySide6 desktop application with two-page interface:
- **ResumeApp class**: Main window with sidebar navigation
- **Resume generation page**: Input fields for company name, job title, and job description
- **Files/history page**: Placeholder for viewing generated resumes
- **UI Framework**: Uses QStackedWidget for page switching, custom styled widgets
- **Generate button handler**: `on_generate()` collects inputs and prepares AI prompt (incomplete implementation at line 241)
- **Dependencies**: Imports `json_template` and `full_base_resume_text` from Utility, `create_request` from Agent

**Utility.py** - Central utility module with document processing:
- **Path configuration**: Uses `pathlib` with centralized `paths` dictionary
- **Global state management**:
  - `base_resumes` - List of Path objects for all base resume .docx files
  - `base_resume_texts` - List of extracted text from each resume
  - `full_base_resume_text` - Concatenated text from all resumes (used for AI prompts)
  - `json_template` - Loaded JSON template dict
  - `resume_template` - Path to Resume Template.docx
- **Document scanning**: `get_base_resumes()` finds all .docx files in BaseResumes/ (filters out `~$` temp files)
- **Text extraction**: `get_docx_text(docx_path)` extracts text from paragraphs, tables, headers, and footers
- **Template loading**: `get_templates()` loads JSON and .docx templates from Resources/
- **Key transformation**: `replace_keys(dict_obj, modifier)` applies lambda functions to dictionary keys
- **Auto-execution**: Runs initialization code on module import (populates all globals)

**Agent.py** - OpenAI API integration:
- **Environment setup**: Loads `.env` file from project root for API keys
- **Client initialization**: Creates OpenAI client instance
- **Model configuration**: Uses `gpt-5` model (configurable via `model` variable)
- **Request function**: `create_request(message)` sends message to OpenAI and returns response content
- **Single-turn conversations**: Each request is stateless (no conversation history)

### Path Configuration

All paths use a centralized dictionary in Utility.py:

```python
base_dir = Path(__file__).parent.parent
paths = {
    "base_resume": base_dir / "BaseResumes",
    "resources": base_dir / "Resources",
    "results": base_dir / "Results"
}
```

### Application Flow

1. **Module Import**: When any module imports Utility.py:
   - All base resumes are scanned and loaded
   - Text is extracted from all resumes and concatenated into `full_base_resume_text`
   - Template files are loaded into memory
   - Global state is initialized

2. **GUI Initialization**: When Main.py runs:
   - PySide6 application window is created with sidebar navigation
   - User inputs company name, job title, and job description
   - On "Generate" button click, `on_generate()` is triggered

3. **Resume Generation** (incomplete implementation):
   - Prompt is constructed with base resume text and job description
   - `create_request()` from Agent.py is called to get AI response
   - Response should be parsed and used to populate `json_template`
   - Final .docx should be generated using `resume_template`

### Template System

**JSON Template** (Resources/Json Template.json):
Structure for resume sections that can be populated:
- Summary
- Job 1/2 Title and Details (arrays)
- Technical Skills
- Personal Project 1/2 and Details (arrays)

**Resume Template** (Resources/Resume Template.docx):
Base .docx file with placeholder formatting to be filled with JSON data

### Key Functions

**get_base_resumes()** - Scans BaseResumes/ folder:
```python
base_resumes = [f for f in folder.glob("*.docx") if not f.name.startswith("~$")]
```

**get_docx_text(docx_path)** - Extracts all text from .docx:
- Returns list of strings from paragraphs and table cells
- Use `'\n'.join(result)` to get single string

**get_templates()** - Loads template files:
- Loads JSON template into `json_template` global
- Sets `resume_template` path

**replace_keys(dict_obj, modifier)** - Transform dictionary keys:
```python
# Example: Wrap keys in curly braces
result = replace_keys(data, lambda s: f"{{{s}}}")
```

## Development

### Setup and Installation

**Windows (using batch scripts)**:
```bash
# Install dependencies
install.bat

# Run application
run.bat
```

**Manual setup (any platform)**:
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python Source/Main.py
```

**Environment Configuration**:
Create a `.env` file in the project root with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

### Python Dependencies

Required packages (see requirements.txt):
- `openai==2.7.1` - OpenAI API client
- `python-dotenv==1.2.1` - Load environment variables from .env
- `python-docx==1.2.0` - Read/write .docx files (import as `from docx import Document`)
- `PySide6==6.10.0` - Qt for Python GUI framework
- `icecream==2.1.4` - Debugging with `ic()`

### Working with Documents

**Text extraction pattern**:
```python
from Source.Utility import get_docx_text
text_list = get_docx_text(file_path)
full_text = '\n'.join(text_list)
```

**File filtering**: Always filter temp files - `.glob("*.docx")` with `if not f.name.startswith("~$")`

**Path handling**: Always use `paths` dictionary from Utility.py, never hardcode paths

### Working with AI Integration

**Making OpenAI API requests**:
```python
from Source.Agent import create_request

# Send a message and get response
response = create_request("Your prompt here")
```

**Current model**: Set to `gpt-5` in Agent.py (line 15). Modify `model` variable to change.

**API configuration**: Requires `OPENAI_API_KEY` in `.env` file at project root.

### GUI Development

**PySide6 structure**:
- Main application in `ResumeApp` class (Main.py)
- Uses `QStackedWidget` for multi-page navigation
- Sidebar buttons switch between pages using `setCurrentIndex()`
- Custom styling via `.setStyleSheet()` with CSS-like syntax

**Adding new pages**:
1. Create page widget with `QWidget()` and layout
2. Add to stacked widget with `self.stacked_widget.addWidget(page)`
3. Create sidebar button that calls `setCurrentIndex()` with page index

### Known Issues & Incomplete Features

**Main.py line 241**: The `on_generate()` method has incomplete implementation - the message string is cut off and needs completion.

**Resume generation pipeline**: Flow from AI response → JSON population → .docx generation is not yet implemented.

**Files/history page**: Currently placeholder with no functionality implemented.
