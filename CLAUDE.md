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
├── Config.json      # Application settings (GPT model, auto-archive, etc.)
├── requirements.txt # Python dependencies
├── install.bat      # Windows installation script
└── run.bat          # Windows run script
```

## Architecture

### Core Modules

**Main.py** - PySide6 desktop application with four-page interface:
- **AIWorker class**: QThread worker for async AI requests without blocking UI
  - Creates separate event loop for async operations
  - Emits `finished` signal with response or `error` signal on failure
  - Keeps GUI responsive during API calls
- **ResumeApp class**: Main window with sidebar navigation (📄 Resume, 🗂️ Files, 📊 Statistics, ⚙️ Settings)
- **Page 0 - Resume generation**: Input fields for company name, job title, and job description
- **Page 1 - Files/History**: Displays generated resumes with filtering (search, match rating, job quality, date range, favorites)
  - Expandable history items showing job details, responsibilities, company size, quality ratings
  - Archive functionality to move JSON files to Archived subfolder
  - Action buttons in expanded view: open folder (📁), generate documents (📝), favorite (⭐)
  - Favorite button shows green background when favorited, white background when not favorited
  - Favorite filter checkbox (⭐ Favorites) to show only favorited items
- **Page 2 - Statistics**: Placeholder for charts and analytics
- **Page 3 - Settings**: Configure GPT model and auto-archive behavior (saved to Config.json)
- **UI Framework**: Uses QStackedWidget for page switching, custom styled widgets with emojis
- **Generate button handler**: `on_generate()` creates AIWorker thread, disables button, updates text to "Generating..." then "Processing Documents..."
- **Response handlers**: `on_ai_response()` processes JSON, saves data, generates resume/cover letter, converts to PDF, plays notification sound; `on_ai_error()` handles errors
- **Dependencies**: Imports `json_template`, `full_base_resume_text`, `resume_template`, `cover_letter_template`, `resume_prompt`, `paths`, `config` from Utility; imports `save_json_obj`, `expand_list_to_keys`, `write_to_docx`, `clear_temp`, `save_document_temp`, `copy_temp_to_results`, `convert_temp_to_pdf`, `get_templates`, `play_notification_sound`, `get_config`, `update_config` from Utility; `create_request`, `model` from Agent

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
- **File copying**: `copy_temp_to_results()` copies all files from Temp to Results, `copy_files(path_a, path_b)` general file copy utility
- **PDF conversion**: `convert_temp_to_pdf()` converts all .docx files in Temp folder to PDFs using docx2pdf
- **Audio notifications**: `play_notification_sound()` plays "Notification Sound.mp3" from Resources folder when resume generation completes
- **Temp management**: `clear_temp()` deletes all files in Temp folder
- **Config management**: `get_config()` loads Config.json, `update_config(config_data)` saves Config.json
- **Archive management**: `archive_json_data(json_file_name)` moves JSON file to Resources/Json Data/Archived subfolder
- **Key transformation**: `replace_keys(dict_obj, modifier, ignore_keys)` applies lambda to dictionary keys
- **Auto-execution**: Runs initialization code on module import (populates all globals)

**Agent.py** - Async OpenAI API integration:
- **Environment setup**: Loads `.env` file from project root for API keys
- **Client initialization**: Creates `AsyncOpenAI()` client instance for async operations
- **Model configuration**: Reads from Config.json via `get_config()['Settings']['GPT Model']` (default: "gpt-5")
- **Async request function**: `async def create_request(message)` sends message to OpenAI with `await`
- **Single-turn conversations**: Each request is stateless (no conversation history)
- **Threading requirement**: Must be called from QThread worker (AIWorker) to avoid blocking GUI
- **API format**: Uses `chat.completions.create()` with role "user" and returns `choices[0].message.content`

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
     - Current date/time for AI context
   - **API Call**: Async request sent to OpenAI (model from Config.json)
   - **Response Handling**:
     - JSON response parsed from AI containing `Meta`, `Resume`, `CoverLetter`, and `Job` sections
     - Lists in Resume section expanded to numbered keys via `expand_list_to_keys()`
     - Meta section updated with file paths, model used, and ISO format date
     - Full JSON (with expanded lists) saved to `Resources/Json Data/` folder for history
   - **Document Generation**:
     - Button text changes to "Processing Documents..."
     - Temp folder cleared via `clear_temp()`
     - Resume data filled into `Resume Template.docx` via `write_to_docx()`
     - Cover letter data filled into `Cover Letter Template.docx`
     - Both .docx files saved to `Temp/` folder
     - All .docx files in Temp/ converted to PDFs via `convert_temp_to_pdf()`
     - All files (both .docx and .pdf) copied from Temp/ to Results/ via `copy_temp_to_results()`
     - Notification sound played via `play_notification_sound()`
   - **UI Update**: Button re-enabled with text "Generate Resume", success message printed

### Template System

**JSON Template** (Resources/Json Template.json):
Four-section structure for AI response:
- **Meta**: File naming (`{Position Title} {Company Name}`), date created, AI notes, resume/cover letter paths (populated by code), favorite status (boolean, default false)
- **Resume**: File name, summary (240-335 chars), 2 jobs with details (arrays of 3-6 items), technical skills (3 categories), certifications, 2 projects with details (arrays of 2 items)
- **CoverLetter**: File name, date, company name, 3 paragraphs
- **Job**: Company name, position title, salary, description (2-3 sentences), tech stack (max 10), job quality (1-10 float with description), company size, responsibilities (array), motive (first-person), match rating (1-10 float with description), date applied (mm/dd/yy), expected response date (mm/dd/yy)

**Resume Template** (Resources/Resume Template.docx):
Base .docx file with placeholder formatting (e.g., `{Summary}`, `{Job1Title}`, `{J1Details1}`)

**Cover Letter Template** (Resources/Cover Letter Template.docx):
Base .docx file with placeholders (e.g., `{CompanyName}`, `{Paragraph1}`)

**Resume Prompt** (Resources/Resume Prompt.md):
Detailed instructions for AI on how to tailor resumes:
- Analyze job description for top 5 technical skills, key responsibilities, soft skills
- Tailor experience using job terminology naturally (avoid AI phrases like "spearheaded", "leveraged")
- Preserve authenticity (concrete numbers, specific technologies, no invented accomplishments)
- Format constraints (1 page, 32 lines max, ~85 chars/line, mix of 1-2 line bullets with only 3-4 two-line bullets)
- Structure priorities (summary 2-3 lines, 2 most relevant jobs, relevant technical skills, 2 projects if relevant)
- Fill minimum array items from JSON template, one sentence per field
- No line breaks in summary, avoid hyphens in cover letter (AI detection concern)
- Write "C#" not "C Sharp" unless ATS requires it

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
json_list = get_json_datas()  # Returns list of parsed JSON objects (excludes Archived subfolder)
```

**archive_json_data(json_file_name)** - Archive a history item:
```python
archive_json_data("Google Software Engineer")  # Moves to Resources/Json Data/Archived/
```

**convert_temp_to_pdf()** - Convert all .docx files in Temp to PDFs:
```python
convert_temp_to_pdf()  # Uses docx2pdf library to create PDFs alongside .docx files
```

**copy_temp_to_results()** - Copy all files from Temp to Results:
```python
copy_temp_to_results()  # Copies both .docx and .pdf files
```

**get_config()** - Load Config.json:
```python
config = get_config()  # Returns dict with Settings and Resources sections
```

**update_config(config_data)** - Save Config.json:
```python
update_config(config)  # Writes config dict to Config.json with indentation
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
- `openai==2.7.1` - OpenAI API client for async chat completions
- `python-dotenv==1.2.1` - Load environment variables from .env file
- `python-docx==1.2.0` - Read/write .docx files (import as `from docx import Document`)
- `docx2pdf` - Convert .docx files to PDF format (used in `convert_temp_to_pdf()`)
- `PySide6==6.10.0` - Qt for Python GUI framework
- `pygame` - Audio playback for notification sounds (via `mixer` module)
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

**Current model**: Configured in Config.json under `Settings.GPT Model` (default: "gpt-5"). Available models listed in `Resources.Available Models` array.

**Model selection**: Users can change the model via Settings page (page 3) in the GUI, which updates Config.json.

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

**History page filtering**:
- Search bar filters by position, company, or tech stack (case-insensitive)
- Min rating dropdown filters by match rating (1-10)
- Min quality dropdown filters by job quality (1-10)
- Date filter dropdown filters by date range (Today, Last 3/7/30 Days, Any day)
- Favorite checkbox filters to show only favorited items
- All filters work together (AND logic) - items must match all active filters
- Filters update title label with visible count and today's count

**History item expansion**:
- Click item to expand/collapse details
- Expanding one item auto-collapses all others (accordion pattern)
- Action buttons in details have `event.accept()` to prevent propagation

### Common Patterns

**Complete document generation workflow** (resume + cover letter + PDF):
```python
# 1. Get AI response (in worker thread)
response = await create_request(prompt)

# 2. Parse JSON response
data = json.loads(response)  # Contains Meta, Resume, CoverLetter, Job sections

# 3. Update metadata with paths and current info
from datetime import datetime
data['Meta']['Resume Path'] = str(paths['results'] / f"{resume_name}.docx")
data['Meta']['Cover Letter Path'] = str(paths['results'] / f"{cover_letter_name}.docx")
data['Meta']['Model Used'] = model  # or get_config()['Settings']['GPT Model']
data['Meta']['Date Created'] = datetime.now().isoformat()
data['Meta']['Favorite'] = False  # Initialize favorite status

# 4. Save complete JSON for history (with expanded lists)
save_json_obj(expand_list_to_keys(data, ""), f"{data['Meta']['File Name']}")

# 5. Process resume section (expand arrays to numbered keys)
resume_data = expand_list_to_keys(data['Resume'], "")
resume_doc = write_to_docx(resume_template, resume_data)

# 6. Process cover letter section (no array expansion needed)
cover_letter_data = data['CoverLetter']
cover_letter_doc = write_to_docx(cover_letter_template, cover_letter_data)

# 7. Clear temp folder, save to temp, convert to PDF, copy to results
clear_temp()
save_document_temp(resume_doc, resume_data['File Name'])
save_document_temp(cover_letter_doc, cover_letter_data['File Name'])
convert_temp_to_pdf()  # Creates PDFs for all .docx in Temp/
copy_temp_to_results()  # Copies both .docx and .pdf to Results/
play_notification_sound()  # Alert user that generation is complete
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
from datetime import datetime

# Reload templates and prompts to get latest versions
get_templates()

# Build comprehensive prompt for AI
current_date_time = datetime.now().strftime("%B %d, %Y %I:%M %p")
message = f"My resumes:\n{full_base_resume_text}\n"  # All base resume text
message += f"Company Name: {company_name}\n Job Title: {job_title}\n Job Description: {job_desc}\n"
message += f"{resume_prompt}"  # Instructions from Resume Prompt.md
message += f"Please respond in a parsable json format that looks like this: \n{json.dumps(json_template)}\n"
message += f"Also make sure to fillout the cover page. The time this request was made is {current_date_time}"

# Send to AI via worker thread
worker = AIWorker(message)
worker.finished.connect(on_ai_response)
worker.start()
```

**Config.json management**:
```python
# Load config
config = get_config()
current_model = config['Settings']['GPT Model']  # e.g., "gpt-5"
auto_archive = config['Settings']['Auto Archive Expired Applications']  # True/False
available_models = config['Resources']['Available Models']  # List of model names

# Update config (used in Settings page)
config['Settings']['GPT Model'] = 'gpt-5-mini'
config['Settings']['Auto Archive Expired Applications'] = True
update_config(config)  # Saves to Config.json with indentation
```

**Archive functionality**:
```python
# Archive a history item (moves JSON from Resources/Json Data/ to Resources/Json Data/Archived/)
file_name = data['Meta']['File Name']  # e.g., "Software Engineer Google"
archive_json_data(file_name)  # Moves "Software Engineer Google.json" to Archived subfolder

# get_json_datas() automatically excludes archived items
datas = get_json_datas()  # Only returns non-archived JSON files
```

**History filtering examples**:
```python
# Filter by date (today's applications)
from datetime import datetime
today = datetime.now().date()
datas_today = [d for d in datas if datetime.fromisoformat(d['Meta']['Date Created']).date() == today]

# Filter by match rating
high_match = [d for d in datas if float(d['Job']['Match Rating']) >= 8]

# Filter by job quality
quality_jobs = [d for d in datas if float(d['Job']['Job Quality']) >= 7]

# Search in tech stack
python_jobs = [d for d in datas if 'Python' in d['Job']['Tech Stack']]
```

**Favorite functionality**:
```python
# Toggle favorite status for a history item
data['Meta']['Favorite'] = not data['Meta'].get('Favorite', False)

# Save the updated JSON
from Utility import save_json_obj, expand_list_to_keys
save_json_obj(expand_list_to_keys(data, ""), f"{data['Meta']['File Name']}")

# Update in-memory history item data for immediate filter response
for item_data in self.history_items:
    if item_data['widget'] == item_widget:
        item_data['favorite'] = data['Meta']['Favorite']
        break

# Visual feedback: Update button style based on favorite status
# Green background (#4CAF50) when favorited, white background when not
```

**Generate documents from history**:
```python
# Regenerate resume and cover letter from saved JSON data
def generate_documents(self, data):
    clear_temp()
    resume_data = data['Resume']  # Already has expanded keys from JSON
    cover_letter_data = data['CoverLetter']

    resume_doc = write_to_docx(resume_template, resume_data)
    cover_letter_doc = write_to_docx(cover_letter_template, cover_letter_data)

    save_document_temp(resume_doc, resume_data['File Name'])
    save_document_temp(cover_letter_doc, cover_letter_data['File Name'])

    convert_temp_to_pdf()
    copy_temp_to_results()
```
