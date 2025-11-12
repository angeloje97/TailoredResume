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
│   ├── Json Data/           # Saved JSON data from AI responses
│   ├── Json Template.json   # Resume data structure template
│   ├── Resume Template.docx # Base resume formatting template
│   ├── Cover Letter Template.docx # Cover letter formatting template
│   └── Resume Prompt.md     # AI prompt instructions for tailoring
├── Results/         # Generated tailored resumes and cover letters (output directory)
├── Temp/            # Temporary document storage during generation
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
- **AIWorker class**: QThread worker for async AI requests without blocking UI
  - Creates separate event loop for async operations
  - Emits `finished` signal with response or `error` signal on failure
  - Keeps GUI responsive during API calls
- **ResumeApp class**: Main window with sidebar navigation
- **Resume generation page**: Input fields for company name, job title, and job description
- **Files/history page**: Placeholder for viewing generated resumes
- **UI Framework**: Uses QStackedWidget for page switching, custom styled widgets
- **Generate button handler**: `on_generate()` creates AIWorker thread, disables button during processing
- **Response handlers**: `on_ai_response()` processes JSON, saves data, generates resume; `on_ai_error()` handles errors
- **Dependencies**: Imports `json_template`, `full_base_resume_text`, `resume_template`, `cover_letter_template`, `resume_prompt`, `save_json_obj`, `expand_list_to_keys`, `write_to_docx`, `save_document_result`, `save_document_temp`, `clear_temp` from Utility; `create_request` from Agent

**Utility.py** - Central utility module with document processing:
- **Path configuration**: Uses `pathlib` with centralized `paths` dictionary
  - `base_resume` - BaseResumes folder
  - `resources` - Resources folder
  - `results` - Results folder (generated documents)
  - `json_data` - Resources/Json Data folder (saved AI responses)
  - `temp` - Temp folder (temporary document storage)
- **Global state management**:
  - `base_resumes` - List of Path objects for all base resume .docx files
  - `base_resume_texts` - List of extracted text from each resume
  - `full_base_resume_text` - Concatenated text from all resumes (used for AI prompts)
  - `json_template` - Loaded JSON template dict
  - `resume_template` - Path to Resume Template.docx
  - `cover_letter_template` - Path to Cover Letter Template.docx
  - `resume_prompt` - Loaded resume prompt instructions from Resume Prompt.md
- **Document scanning**: `scan_docx(docx_path, modifier)` - Read-only iteration with callback, returns Document
- **Document modification**: `modify_docx(docx_path, modifier)` - Transforms text in paragraphs, tables, headers, footers
- **Text extraction**: `get_docx_text(docx_path)` uses `scan_docx` to collect text into list
- **Template filling**: `write_to_docx(template_path, data)` fills placeholders and returns Document
- **String replacement**: `fill_template(template_string, data)` replaces `{key}` placeholders with values
- **Data transformation**: `expand_list_to_keys(obj, separator)` converts list values to numbered keys
- **JSON operations**: `save_json_obj()` saves to json_data folder, `get_json_datas()` loads all JSON files
- **Document saving**: `save_document_result(doc, name)` saves Document to Results folder, `save_document_temp(doc, name)` saves to Temp folder
- **Temp management**: `clear_temp()` deletes all files in Temp folder
- **Key transformation**: `replace_keys(dict_obj, modifier, ignore_keys)` applies lambda to dictionary keys
- **Auto-execution**: Runs initialization code on module import (populates all globals)

**Agent.py** - Async OpenAI API integration:
- **Environment setup**: Loads `.env` file from project root for API keys
- **Client initialization**: Creates `AsyncOpenAI()` client instance for async operations
- **Model configuration**: Uses `gpt-5` model (configurable via `model` variable at line 15)
- **Async request function**: `async def create_request(message)` sends message to OpenAI with `await`
- **Single-turn conversations**: Each request is stateless (no conversation history)
- **Threading requirement**: Must be called from QThread worker (AIWorker) to avoid blocking GUI

### Path Configuration

All paths use a centralized dictionary in Utility.py:

```python
base_dir = Path(__file__).parent.parent
paths = {
    "base_resume": base_dir / "BaseResumes",
    "resources": base_dir / "Resources",
    "results": base_dir / "Results",
    "json_data": base_dir / "Resources" / "Json Data",
    "temp": base_dir / "Temp"
}
```

### Application Flow

1. **Module Import**: When any module imports Utility.py:
   - All base resumes are scanned and loaded
   - Text is extracted from all resumes and concatenated into `full_base_resume_text`
   - Template files (JSON, .docx, and Resume Prompt.md) are loaded into memory
   - Global state is initialized
   - Ensures all required folders exist

2. **GUI Initialization**: When Main.py runs:
   - PySide6 application window is created with sidebar navigation
   - User inputs company name, job title, and job description
   - On "Generate" button click, `on_generate()` is triggered

3. **Async Document Generation** (complete pipeline):
   - **UI Thread**: Button disabled, text changes to "Generating..."
   - **Worker Thread**: AIWorker created with AI prompt combining:
     - `full_base_resume_text` (all base resumes)
     - User inputs (company name, job title, job description)
     - `resume_prompt` (instructions from Resume Prompt.md)
     - `json_template` structure for expected response format
   - **API Call**: Async request sent to OpenAI (gpt-5 model)
   - **Response Handling**:
     - JSON response parsed from AI containing `Meta`, `Resume`, and `CoverLetter` sections
     - Lists in Resume section expanded to numbered keys via `expand_list_to_keys()`
     - Full JSON saved to `Resources/Json Data/` folder for history
   - **Document Generation**:
     - Resume data filled into `Resume Template.docx` via `write_to_docx()`
     - Cover letter data filled into `Cover Letter Template.docx`
     - Both documents saved to `Results/` folder (permanent storage)
     - Both documents saved to `Temp/` folder (temporary workspace)
   - **UI Update**: Button re-enabled, success message displayed

### Template System

**JSON Template** (Resources/Json Template.json):
Three-section structure for AI response:
- **Meta**: File naming, company/position info, date, AI notes
- **Resume**: Summary, 2 jobs with details (arrays), technical skills, 2 projects with details (arrays)
- **CoverLetter**: Date, company name, 3 paragraphs

**Resume Template** (Resources/Resume Template.docx):
Base .docx file with placeholder formatting (e.g., `{Summary}`, `{Job1Title}`, `{J1Details1}`)

**Cover Letter Template** (Resources/Cover Letter Template.docx):
Base .docx file with placeholders (e.g., `{CompanyName}`, `{Paragraph1}`)

**Resume Prompt** (Resources/Resume Prompt.md):
Detailed instructions for AI on how to tailor resumes:
- Analyze job description for required skills and responsibilities
- Tailor experience using job terminology
- Preserve authenticity (no exaggeration, concrete numbers)
- Format constraints (1 page, 32 lines, ~93 chars/line)
- Structure priorities (summary, relevant jobs/projects only)

### Document Processing Pattern

The codebase uses a clean separation between reading and modifying documents:

**scan_docx(docx_path, modifier)** - Read-only document iteration:
```python
def scan_docx(docx_path, modifier) -> Document:
    # Calls modifier(text) for each text element
    # Returns document unchanged (for chaining)
```

**modify_docx(docx_path, modifier) -> Document** - Document transformation:
```python
def modify_docx(docx_path, modifier) -> Document:
    # For each text element: element.text = modifier(element.text)
    # Returns modified document
```

Both iterate over: paragraphs, table cells, headers, footers.

### Key Functions

**expand_list_to_keys(obj, separator)** - Convert lists to numbered keys:
```python
# Input:  {"details": [1, 2, 3], "name": "John"}
# Output: {"details 1": 1, "details 2": 2, "details 3": 3, "name": "John"}
expand_list_to_keys(data, " ")
```

**write_to_docx(template_path, data) -> Document** - Fill template with data:
```python
# Wraps keys in {braces}, replaces placeholders, returns Document
doc = write_to_docx(template_path, {"Name": "John", "Title": "Engineer"})
```

**fill_template(template_string, data) -> str** - String replacement:
```python
# Replaces all occurrences of keys with values
result = fill_template("Hello {Name}", {"{Name}": "John"})  # "Hello John"
```

**save_document_result(doc, name)** - Save Document to Results/ (permanent storage):
```python
save_document_result(doc, "Google_Resume")  # Saves to Results/Google_Resume.docx
```

**save_document_temp(doc, name)** - Save Document to Temp/ (temporary workspace):
```python
save_document_temp(doc, "Google_Resume")  # Saves to Temp/Google_Resume.docx
```

**clear_temp()** - Delete all files in Temp/ folder:
```python
clear_temp()  # Removes all temporary files
```

**get_json_datas()** - Load all JSON files from json_data folder:
```python
json_list = get_json_datas()  # Returns list of parsed JSON objects
```

**replace_keys(dict_obj, modifier, ignore_keys)** - Transform dictionary keys:
```python
# Example: Wrap keys in curly braces
result = replace_keys(data, lambda s: f"{{{s}}}", ignore_keys=["special"])
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

**Making async OpenAI API requests**:

Agent.py uses `AsyncOpenAI` and must be called from a QThread worker:

```python
import asyncio
from Source.Agent import create_request

# Must run in async context (like AIWorker.run())
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
response = loop.run_until_complete(create_request("Your prompt here"))
loop.close()
```

**Using AIWorker (recommended)**:
```python
# Create worker thread
worker = AIWorker(message)
worker.finished.connect(on_response_callback)
worker.error.connect(on_error_callback)
worker.start()

def on_response_callback(response_text):
    # Handle response in main GUI thread
    pass
```

**Current model**: Set to `gpt-5` in Agent.py (line 15). Modify `model` variable to change.

**API configuration**: Requires `OPENAI_API_KEY` in `.env` file at project root.

**Why async + QThread**:
- `AsyncOpenAI` provides better performance and connection pooling
- QThread keeps GUI responsive during API calls
- Signals/slots enable thread-safe communication

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

### Common Patterns

**Complete document generation workflow** (resume + cover letter):
```python
# 1. Get AI response (in worker thread)
response = await create_request(prompt)

# 2. Parse JSON response
data = json.loads(response)  # Contains Meta, Resume, CoverLetter sections

# 3. Save complete JSON for history
save_json_obj(expand_list_to_keys(data, ""), f"{data['Meta']['File Name']} Data")

# 4. Process resume section (expand arrays to numbered keys)
resume_data = expand_list_to_keys(data['Resume'], "")
resume_doc = write_to_docx(resume_template, resume_data)

# 5. Process cover letter section (no array expansion needed)
cover_letter_data = data['CoverLetter']
cover_letter_doc = write_to_docx(cover_letter_template, cover_letter_data)

# 6. Save both documents to Results/ and Temp/
save_document_result(resume_doc, resume_data['File Name'])
save_document_result(cover_letter_doc, cover_letter_data['File Name'])
save_document_temp(resume_doc, resume_data['File Name'])
save_document_temp(cover_letter_doc, cover_letter_data['File Name'])
```

**Working with document templates**:
```python
# Template should have placeholders like: {Name}, {Job1Title}, {J1Details1}
# Data should be flat dict (no nested lists after expand_list_to_keys)
data = {
    "Name": "John Doe",
    "Job1Title": "Software Engineer",
    "J1Details1": "Built scalable systems"
}

doc = write_to_docx(template_path, data)
save_document_result(doc, "output_name")
```

**Understanding expand_list_to_keys behavior**:
```python
# IMPORTANT: separator="" means NO separator between key and number
data = {"J1Details": ["Detail 1", "Detail 2"]}
result = expand_list_to_keys(data, "")
# Result: {"J1Details1": "Detail 1", "J1Details2": "Detail 2"}

# If separator=" " was used:
result = expand_list_to_keys(data, " ")
# Result: {"J1Details 1": "Detail 1", "J1Details 2": "Detail 2"}
```

**AI Prompt Construction** (see Main.py on_generate() method):
```python
# Build comprehensive prompt for AI
message = f"My resumes:\n{full_base_resume_text}\n"  # All base resume text
message += f"Company Name: {company_name}\n Job Title: {job_title}\n Job Description: {job_desc}\n"
message += f"{resume_prompt}"  # Instructions from Resume Prompt.md
message += f"Please respond in a parsable json format that looks like this: \n{json.dumps(json_template)}\n"
message += "Also make sure to fillout the cover page"

# Send to AI via worker thread
worker = AIWorker(message)
worker.finished.connect(on_ai_response)
worker.start()
```
