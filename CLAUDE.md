# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Windows desktop application (PySide6 GUI) that tailors resumes and cover letters for specific job applications using AI. It supports both OpenAI and Anthropic models, generates `.docx` + PDF output from `.docx` templates, and tracks application history (with match/quality ratings, favorites, and archiving) as JSON files on disk — there is no database.

## Commands

```bash
# Install dependencies (Windows)
install.bat
# or manually:
pip install -r requirements.txt

# Run the application
run.bat
# or manually:
python Source/Main.py
```

There is no test runner, linter, or build step configured. `Source/Test.py` is a small ad-hoc script, not a test suite (no pytest/unittest scaffolding).

**Environment**: requires a `.env` file in the project root with `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY`, depending on which model is selected in `Config.json`.

## Architecture

### Module responsibilities

- **`Source/Main.py`** — PySide6 GUI, single entry point. `ResumeApp` (QMainWindow) hosts a `QStackedWidget` with pages: Resume generation, Files (history), Archive, Statistics (placeholder), Settings. `AIWorker` (QThread) runs `Agent.create_request` on a background event loop so the GUI thread never blocks on network calls.
- **`Source/Agent.py`** — Provider-agnostic AI request layer. `create_request(message)` reads `Config.json`'s `Settings.Current Model` and routes to `create_gpt_request` (OpenAI, `AsyncOpenAI`) or `create_claude_request` (Anthropic, `AsyncAnthropic`) based on whether the model name contains `"gpt"` or `"claude"`. Claude responses are passed through `strip_markdown_code_fence` since Claude sometimes wraps JSON in ` ```json ` fences; OpenAI responses are not.
- **`Source/Utility.py`** — Central utility module: path config, `.docx` scanning/templating, JSON persistence (history, archive), PDF conversion, config load/save, notification sound. Runs initialization code at import time (see below) — importing this module has side effects.
- **`Source/Widgets.py`** — Reusable styled PySide6 widget factories (`SideBarButton`, `InputText`, `InputTextBox`, `LabelDescription`, `SettingsCheckbox`, etc.) used to avoid repeating `.setStyleSheet()` boilerplate across pages.

### Import-time initialization (`Utility.py`)

Importing `Utility` (directly or transitively) executes, in order: `get_base_resumes()` → `get_templates()` → `get_resume_full_resume_text()` → `get_config()` → `get_json_datas()` → `copy_temp_to_results()` → (if enabled) `archive_expired_datas()`. This means simply importing the module scans `BaseResumes/`, loads all prompt/template files, loads `Config.json`, and can move files between `Temp/`/`Results/`/`Archived/`. Be aware of this when writing scripts or tests that import `Utility` — there's no lazy/guarded init.

### Multi-provider AI configuration

`Config.json` structure:
```json
{
    "Settings": {
        "Auto Archive Expired Applications": true,
        "Auto Archive Expired Favorite Applications": false,
        "Current Model": "claude-sonnet-5"
    },
    "Resources": {
        "Available Models": ["gpt-5", "gpt-5-mini", "claude-sonnet-5", "claude-opus-4-8", "...": "..."]
    }
}
```
- The setting key is `Current Model` (not `GPT Model`) — it holds either an OpenAI or Anthropic model id.
- `Agent.create_request` dispatches purely on substring match (`"claude" in model` / `"gpt" in model`), so any new model added to `Available Models` must contain one of those substrings to route correctly.
- The Settings page dropdown writes straight back to `Config.json` via `update_config()`.

### Three-stage generation flow

The Resume page separates rating from generation so a user can preview fit before spending tokens on a full tailored resume:

1. **Check Rating** (`on_check_rating` → `on_rating_response` → `show_rating_modal`): sends job title/company/description plus `Resources/Match Rating Prompt.md` and `Resources/Job Quality Prompt.md` to the AI, gets back `Match Rating`/`Job Quality` (1–10) plus text descriptions, and shows them in a modal dialog with **Close** / **Generate Resume** buttons.
2. **Generate from modal** (`generate_btn` → `dialog.accept()` → `on_generate(with_rating=False)`): reuses the rating already computed (stored on `self.current_match_rating` etc.) instead of asking the AI to re-derive it, and injects it directly into `json_template['Job']` before the tailoring request.
3. **Generate directly** (`on_generate(with_rating=True)`, the default): skips the rating modal and asks the AI to compute Match Rating/Job Quality *and* the tailored resume/cover letter in the same request.

`on_generate` always calls `get_templates()` first to reload prompt/template files from disk, so editing `Resources/*.md` or `Resources/Json Template.json` takes effect without restarting the app.

### Save Submission mode

The Resume page has a "Save Submission" checkbox (plus an Application Link field). When checked, `on_ai_response` saves the JSON history record but **skips** `write_to_docx`/`convert_temp_to_pdf`/`copy_temp_to_results` — used for logging job applications that don't need a freshly generated document (e.g., applying without a tailored resume, or re-logging separately).

### Document processing pattern (`Utility.py`)

Two structurally similar traversal functions over paragraphs, table cells, and headers/footers:
- **`scan_docx(docx_path, modifier)`** — read-only; calls `modifier(text)` per element for side effects (e.g., text extraction), returns the `Document` unchanged.
- **`modify_docx(docx_path, modifier)`** — replaces each paragraph's combined run text with `modifier(full_text)`, collapsing multi-run paragraphs into a single run (this loses any run-level formatting differences within a paragraph, e.g. partial bold/italic).

`write_to_docx(template_path, data)` wraps all data keys in `{braces}` and calls `modify_docx` with `fill_template`, so `.docx` templates use `{PlaceholderName}` tokens (see `Resources/Resume Template.docx`, `Resources/Cover Letter Template.docx`).

### History/Archive data model

- Each generated (or "saved submission") application is one JSON file in `Resources/Json Data/`, named after `Meta['File Name']`. Archived items live in `Resources/Json Data/Archived/` — `get_json_datas()` only reads the top-level folder, `get_archived_datas()` only reads `Archived/`.
- JSON has four top-level sections: `Meta` (file paths, model used, date created, `Favorite` bool), `Resume`, `CoverLetter`, `Job` (includes `Match Rating`, `Job Quality`, `Expected Response Date` as `mm/dd/yy`, `Save Submission`, `Application Link`).
- List-valued fields (e.g., job detail bullets) are flattened via `expand_list_to_keys(obj, separator)` before saving/templating, since `.docx` templates can only match flat string keys — e.g. `{"J1Details": [...]}` with `separator=""` becomes `J1Details1`, `J1Details2`, ...
- Archiving (`archive_json_data`) and restoring (`restore_archive_data`) both use `shutil.move` with a `"{name} Data.json"` backup-path fallback if the primary move fails — this fallback naming convention only makes sense if you know some history entries were saved under that suffixed name historically; don't assume it's dead code.
- `archive_expired_datas()` runs automatically on startup (via `Utility.py` import-time init) if `Auto Archive Expired Applications` is enabled in Config.json, comparing `Job['Expected Response Date']` to now; favorites are skipped unless `Auto Archive Expired Favorite Applications` is also enabled.
- Deleting a history item (`delete_history_item` in Main.py) is a permanent `os.remove` of the JSON file after a confirmation `QMessageBox` — there is no undo/trash, unlike archiving.

### GUI page structure (`Main.py`, `ResumeApp`)

- Pages are added to a `QStackedWidget`; sidebar buttons (`create_sidebar`) call `setCurrentIndex()`.
- **Files/Archive pages** use an accordion pattern: expanding one history/archive item auto-collapses the others (`collapse_all_history_items`). Action buttons inside an expanded item call `event.accept()` to stop the click from also toggling collapse/expand.
- **Filtering** (`filter_history_items` / `filter_archive_items`) combines search text, min match rating, min job quality, date range, and favorite-only with AND logic, and updates a visible-count label.
- Dialogs (rating modal, date-update dialog, delete confirmation) are built inline inside their handler methods with local imports of `QDialog`/etc. rather than as separate classes/files — follow this pattern for new modals unless there's a strong reason to extract one.

## Working with documents and templates

- Always filter out Word's transient lock files when globbing `.docx`: `folder.glob("*.docx")` results still need `if not f.name.startswith("~$")`.
- Never hardcode paths — use the `paths` dict from `Utility.py` (`base_resume`, `resources`, `results`, `json_data`, `temp`).
- Template placeholders are case-sensitive `{PlaceholderName}` tokens; `write_to_docx` only replaces string-valued data keys (`fill_template` skips non-`str` values), so numeric/bool fields must be stringified before being passed in if they need to land in a template.
