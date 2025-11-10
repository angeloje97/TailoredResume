# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python automation tool for tailoring resumes. The project processes base resume templates from `BaseResumes/` and generates customized versions in `Results/`.

## Project Structure

```
.
├── BaseResumes/     # Source resume templates (.docx files)
│   └── Resume2025_*.docx  # Latest resume versions (D, M, 3 variants)
├── Resources/       # Supporting resources (job descriptions, templates, etc.)
├── Results/         # Generated tailored resumes
└── Source/          # Python source code
    ├── Main.py      # Entry point for the application
    └── Utility.py   # Utility functions for resume processing
```

## Architecture

### Core Modules

**Utility.py** - Central utility module with document processing functions:
- **Path configuration**: Uses `pathlib` with centralized `paths` dictionary
- **Global state management**: Stores loaded resumes, templates, and extracted text
- **Document scanning**: `get_base_resumes()` finds all .docx files in BaseResumes/ (filters out `~$` temp files)
- **Text extraction**: `get_docx_text(docx_path)` extracts text from paragraphs and tables
- **Template loading**: `get_templates()` loads JSON and .docx templates from Resources/
- **Key transformation**: `replace_keys(dict_obj, modifier)` applies lambda functions to dictionary keys
- **Auto-execution**: Runs initialization code on module import

**Main.py** - Application entry point (currently empty, orchestration logic goes here)

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

### Global State Variables

Utility.py maintains these globals (populated on import):
- `base_resumes` - List of Path objects for all base resume .docx files
- `base_resume_texts` - List of extracted text from resumes
- `json_template` - Loaded JSON template dict from Resources/Json Template.json
- `resume_template` - Path to Resume Template.docx

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

### Running the Application

```bash
python Source/Main.py
```

### Python Dependencies

```bash
pip install icecream python-docx
```

Required packages:
- `python-docx` - Read/write .docx files (import as `from docx import Document`)
- `icecream` - Debugging with `ic()`
- `pathlib`, `json` - Standard library

### Working with Documents

**Text extraction pattern**:
```python
from Source.Utility import get_docx_text
text_list = get_docx_text(file_path)
full_text = '\n'.join(text_list)
```

**File filtering**: Always filter temp files - `.glob("*.docx")` with `if not f.name.startswith("~$")`

**Path handling**: Always use `paths` dictionary, never hardcode paths
