from pathlib import Path
from icecream import ic
from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.hyperlink import Hyperlink
from docx.text.paragraph import Paragraph
from docx2pdf import convert
from pygame import mixer
import json
import re
import shutil
import os
import threading
from datetime import datetime

#region Global Variables

base_dir = Path(__file__).parent.parent

paths = {
    "base_resume": base_dir / "BaseResumes",
    "resources": base_dir / "Resources",
    "results": base_dir / "Results",
    "json_data" : base_dir / "Resources" / "Json Data",
    "temp": base_dir / "Temp"
}

base_resumes = []
base_resume_texts = []
full_base_resume_text = ""
resume_prompt = ""
match_rating_prompt = ""
job_quality_prompt = ""


json_template = {}
resume_template = ""
cover_letter_template = ""

config = {}

#endregion

#region Functions

def get_base_resumes():
    global paths
    global base_resumes

    folder = Path(paths["base_resume"])
    ensure_path_exists(folder)

    base_resumes = [f for f in folder.glob("*.docx") if not f.name.startswith("~$")]

def scan_docx(docx_path, modifier) -> Document:
    doc = Document(docx_path)
    
    for paragraph in doc.paragraphs:
        modifier(paragraph.text)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                modifier(cell.text)

    for section in doc.sections:
        for paragraph in section.header.paragraphs:
            if paragraph.text.strip():
                modifier(paragraph.text)

        for paragraph in section.footer.paragraphs:
            if paragraph.text.strip():
                modifier(paragraph.text)

    return doc

def modify_docx(docx_path, modifier) -> Document:
    doc = Document(docx_path)

    def process_paragraph(paragraph):
        full_text = ''.join(run.text for run in paragraph.runs)

        modified_text = modifier(full_text)
        
        applied_text = False
        for run in paragraph.runs:
            run.text = ""

            if not applied_text:
                applied_text = True
                paragraph.runs[0].text = modified_text
        
    for paragraph in doc.paragraphs:
        process_paragraph(paragraph)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    process_paragraph(paragraph)
                        
    for section in doc.sections:
        for paragraph in section.header.paragraphs:
            if paragraph.text.strip():
                process_paragraph(paragraph)
                    

        for paragraph in section.footer.paragraphs:
            if paragraph.text.strip():
                process_paragraph(paragraph)
                    

    return doc

#region Docx text extraction (for feeding documents to the AI)

_MC_FALLBACK = '{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback'

def _paragraph_line(paragraph) -> str:
    """One paragraph as a line of text, marking headings ('# ') and list items ('- ') and keeping link URLs."""
    parts = []
    for item in paragraph.iter_inner_content():
        if isinstance(item, Hyperlink):
            url = item.url
            parts.append(f"{item.text} ({url})" if url and url not in item.text else item.text)
        else:
            parts.append(item.text)
    text = re.sub(r'\s+', ' ', ''.join(parts)).strip()
    if not text:
        return ""

    style = paragraph.style.name if paragraph.style is not None else ""
    if style == "Title":
        return f"# {text}"
    if style.startswith("Heading"):
        level = style.split()[-1]
        return f"{'#' * (int(level) + 1 if level.isdigit() else 2)} {text}"
    has_numbering = paragraph._p.pPr is not None and paragraph._p.pPr.numPr is not None
    if has_numbering or "List" in style:
        return f"- {text}"
    return text

def _text_boxes(p_element):
    """Text box contents inside a paragraph, skipping the duplicate legacy (VML) copy Word saves alongside."""
    for box in p_element.iter(qn('w:txbxContent')):
        if not any(ancestor.tag == _MC_FALLBACK for ancestor in box.iterancestors()):
            yield box

def _table_lines(table):
    lines = []
    for row in table.rows:
        seen = set()
        cells = []
        for cell in row.cells:
            # Merged cells are returned once per column they span
            if id(cell._tc) in seen:
                continue
            seen.add(id(cell._tc))
            cells.append(list(_block_lines(cell._tc, cell)))

        if all(len(cell) <= 1 for cell in cells):
            # Data-style row: keep the columns together on one line
            row_text = " | ".join(cell[0] for cell in cells if cell)
            if row_text:
                lines.append(row_text)
        else:
            # Layout table (common in resumes): read each cell top to bottom
            for cell in cells:
                lines.extend(cell)
    return lines

def _block_lines(container, parent):
    """Lines for the paragraphs/tables in a body, cell, header, or text box, in document order."""
    for child in container.iterchildren():
        if child.tag == qn('w:p'):
            line = _paragraph_line(Paragraph(child, parent))
            if line:
                yield line
            for box in _text_boxes(child):
                yield from _block_lines(box, parent)
        elif child.tag == qn('w:tbl'):
            yield from _table_lines(Table(child, parent))
        elif child.tag == qn('w:sdt'):
            # Content controls wrap ordinary paragraphs/tables
            content = child.find(qn('w:sdtContent'))
            if content is not None:
                yield from _block_lines(content, parent)

def get_docx_text(docx_path) -> list[str]:
    """
    Readable text of a .docx for the AI, in document order: headers, body (paragraphs, tables, text boxes), footers.
    Headings are prefixed with '#', list items with '- ', and hyperlinks keep their URL.
    """
    doc = Document(docx_path)

    def header_footer_lines(parts):
        lines = []
        for part in parts:
            # Sections usually share (link to) the same header/footer, so skip repeats
            if part.is_linked_to_previous and lines:
                continue
            lines.extend(line for line in _block_lines(part._element, part) if line not in lines)
        return lines

    return (header_footer_lines(section.header for section in doc.sections)
            + list(_block_lines(doc.element.body, doc))
            + header_footer_lines(section.footer for section in doc.sections))

#endregion

def get_templates():
    global paths
    global resume_template
    global json_template
    global cover_letter_template
    global resume_prompt
    global match_rating_prompt
    global job_quality_prompt

    prompt_path = paths['resources'] / "Resume Prompt.md"
    match_rating_prompt_path = paths['resources'] / "Match Rating Prompt.md"
    job_quality_prompt_path = paths['resources'] / "Job Quality Prompt.md"
    json_path = paths['resources'] / "Json Template.json"
    resume_template = paths['resources'] / "Resume Template.docx"
    cover_letter_template = paths['resources'] / "Cover Letter Template.docx"

    with open(json_path, "r", encoding="utf-8") as file:
        json_template = json.load(file)

    with open(prompt_path, 'r', encoding="utf-8") as file:
        resume_prompt = file.read()

    with open(match_rating_prompt_path, 'r', encoding="utf-8") as file:
        match_rating_prompt = file.read()

    with open(job_quality_prompt_path, 'r', encoding="utf-8") as file:
        job_quality_prompt = file.read()

    # Re-read BaseResumes too, so added/edited/moved resumes apply without restarting
    get_resume_full_resume_text()

def get_json_datas():
    global paths
    json_datas = []
    ensure_path_exists(paths["json_data"])

    # Only get JSON files in the json_data folder, not in subdirectories (like Archived)
    json_paths = [p for p in paths['json_data'].glob("*.json") if p.is_file()]

    for path in json_paths:
        with open(path, 'r', encoding="utf-8") as file:
            json_datas.append(json.load(file))

    return json_datas

def get_archived_datas():
    global paths

    archived_path = paths['json_data'] / "Archived"

    ensure_path_exists(archived_path)

    json_paths = [p for p in archived_path.glob("*.json") if p.is_file()]
    datas = []
    for path in json_paths:
        with open(path, 'r', encoding='utf-8') as file:
            datas.append(json.load(file))
    return datas

def archive_expired_datas():
    global paths
    global config

    expired_datas = []
    current_date = datetime.now()

    ensure_path_exists(paths['json_data'])

    # Check if we should also archive expired favorites
    archive_favorites = config.get('Settings', {}).get('Auto Archive Expired Favorite Applications', False)

    json_paths = [p for p in paths['json_data'].glob("*.json") if p.is_file()]

    for path in json_paths:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)

            try:
                expected_date = data['Job']['Expected Response Date']
                date = datetime.strptime(expected_date, "%m/%d/%y")
                is_favorite = data['Meta'].get('Favorite', False)

                # Archive if expired and either not a favorite, or archiving favorites is enabled
                if current_date > date and (not is_favorite or archive_favorites):
                    expired_datas.append(path.stem)
            except Exception as e:
                print("Does not have expected response date")

    for file_name in expired_datas:
        archive_json_data(file_name)

def restore_archive_data(json_file_name):
    global paths

    full_path = paths['json_data'] / f'Archived' / f"{json_file_name}.json"
    back_up_path = paths['json_data'] / f'Archived' / f"{json_file_name} Data.json"

    destination_path = paths['json_data']

    try:
        shutil.move(full_path, destination_path)
        
    except Exception as e1:
        print(f"Something went wrong with moving {json_file_name}, using backup now\n{e1}")
        try:
            shutil.move(back_up_path, destination_path)

        except Exception as e2:
            print(f"Something went wrong when moving backup path\n{e2}")


def archive_json_data(json_file_name):
    full_path = paths['json_data'] / f"{json_file_name}.json"
    destination_path = paths['json_data'] / 'Archived'

    backup_path = paths['json_data'] / f"{json_file_name} Data.json"

    ensure_path_exists(destination_path)
    try:

        shutil.move(full_path, destination_path)

    except Exception as e1:

        print(f"Trouble moving{json_file_name}\n{e1}")
        print(f"Using backup path {backup_path}")

        try:

            shutil.move(backup_path, destination_path) 

        except Exception as e2:

            print(f"Trouble moving backup path\n{e2}")


def get_config():
    global base_dir
    global config
    full_path = base_dir / "Config.json"

    with open(full_path, 'r', encoding="utf-8") as file:
        config = json.load(file)
    
    return config

def update_config(config_data):
    global base_dir
    full_path = base_dir / "Config.json"

    with open(full_path, 'w', encoding='utf-8') as file:
        json.dump(config_data, file, indent=4, ensure_ascii=False)


def save_document_result(doc: Document, name: str):
    global paths

    full_path = paths["results"] / f'{name}.docx'

    doc.save(full_path)

def save_document_temp(doc: Document, name: str):
    global paths

    ensure_path_exists(paths['temp'])

    full_path = paths['temp'] / f'{name}.docx'

    doc.save(full_path)

def copy_files(path_a, path_b):
    ensure_path_exists(path_a)
    ensure_path_exists(path_b)

    for file_name in os.listdir(path_a):
        src_path = os.path.join(path_a, file_name)
        dst_path = os.path.join(path_b, file_name)

        if os.path.isfile(src_path):
            shutil.copy2(src_path, dst_path)

def copy_temp_to_results():
    global paths

    copy_files(paths['temp'], paths['results'])

def clear_temp():
    global paths
    temp_path = paths['temp']

    for file in Path(temp_path).glob("*"):
        try:
            if file.is_file():
                file.unlink()
        except Exception as e:
            print(f"Could not remove {file.name}\n{e}")

def convert_temp_to_pdf():
    global paths

    path = paths['temp']

    # docx2pdf drives Word over COM, which must be initialized on whichever thread calls it
    # (the GUI thread already has it; background threads don't)
    com_initialized = False
    if os.name == 'nt':
        import pythoncom
        pythoncom.CoInitialize()
        com_initialized = True

    try:
        for file in os.listdir(path):
            if not file.lower().endswith(".docx"):
                continue

            input_path = os.path.join(path, file)
            output_path = os.path.join(path, file.replace(".docx", ".pdf"))

            convert(input_path, output_path)
    finally:
        if com_initialized:
            pythoncom.CoUninitialize()

# Temp/ is shared, so only one document build may run at a time
_build_documents_lock = threading.Lock()

def build_documents(resume_data: dict, cover_letter_data: dict):
    """
    Fill the resume + cover letter templates, convert both to PDF, and copy them to Results/.

    Slow (Word is launched for the PDF conversion), so call it from a background thread.
    `resume_data` must already be flattened with expand_list_to_keys. Concurrent calls wait their turn.
    """
    with _build_documents_lock:
        clear_temp()

        resume_doc = write_to_docx(resume_template, resume_data)
        cover_letter_doc = write_to_docx(cover_letter_template, cover_letter_data)

        save_document_temp(resume_doc, resume_data['File Name'])
        save_document_temp(cover_letter_doc, cover_letter_data['File Name'])

        convert_temp_to_pdf()

        copy_temp_to_results()

def sanitize_file_name(name):
    """Make an AI-generated name safe as a Windows file name, e.g. "Engineer (React / Next.js)" -> "Engineer (React - Next.js)"."""
    name = re.sub(r'\s*[\\/|]\s*', ' - ', str(name))          # separators read naturally as a dash
    name = re.sub(r'[<>:"?*\x00-\x1f]', '', name)              # other characters Windows forbids
    name = re.sub(r'\s+', ' ', name).strip(' .')               # no trailing dots/spaces on Windows
    if re.fullmatch(r'(?i)(con|prn|aux|nul|com\d|lpt\d)(\..*)?', name):
        name = f"_{name}"                                      # reserved device names
    return name[:150] or "Untitled"

def save_json_obj(obj, file_name):
    global paths

    ensure_path_exists(paths["json_data"])
    full_path = paths["json_data"] / f"{file_name}.json"


    with open(full_path, 'w', encoding='utf-8') as file:
        json.dump(obj, file, indent=4, ensure_ascii=False)

def expand_list_to_keys(obj, seperator=""):
    result = {}

    for key, value in obj.items():
        if not isinstance(value, list):
            result[key] = value
            continue

        for i, item in enumerate(value, start = 1):
            result[f"{key}{seperator}{i}"] = item

        
    return result

def ensure_path_exists(path):
    folder_path = Path(path)
    folder_path.mkdir(exist_ok=True)

def replace_keys(dict_obj, modifier, ignore_keys=[]):
    result = {}

    for key, value in dict_obj.items():
        if key in ignore_keys:
            result[key] = value
            continue
        new_key = modifier(key)
        result[new_key] = value

    return result

def write_to_docx(template_path: str, data: object) -> Document:
    modified_data = replace_keys(data, lambda s: "{" + s + "}")
    
    return modify_docx(template_path, lambda s: fill_template(s, modified_data))

def fill_template(template_string: str, data: object) -> str:
    new_string = template_string
    for key, val in data.items():
        if not isinstance(val, str):
            continue
        new_string = new_string.replace(key, val)

    return new_string

def get_resume_full_resume_text() -> str:
    global full_base_resume_text
    global base_resumes

    get_base_resumes()

    full_base_resume_text = ''
    base_resume_texts.clear()

    for resume in base_resumes:
        try:
            text = '\n'.join(get_docx_text(resume))
        except Exception as e:
            # One unreadable file shouldn't block every request
            print(f"Could not read {resume.name}, skipping it\n{e}")
            continue
        base_resume_texts.append(text)
        full_base_resume_text += f"\n{'-'*50}\n{resume.name}\n{'-'*50}\n{text}\n"

    return full_base_resume_text

def play_sound(mp3_path: str):
    mixer.init()
    mixer.music.load(mp3_path)
    mixer.music.play()

def play_notification_sound():
    full_path = paths['resources'] / "Notification Sound.mp3"

    play_sound(full_path)
#endregion

#region Main Script

get_base_resumes()
get_templates()  # also loads the BaseResumes text

# Populate base resume texts
get_config()

get_json_datas()

copy_temp_to_results()

if(config['Settings']['Auto Archive Expired Applications']):
    archive_expired_datas()

#endregion
