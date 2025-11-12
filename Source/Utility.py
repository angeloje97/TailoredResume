from pathlib import Path
from icecream import ic
from docx import Document
import json


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


json_template = {}
resume_template = ""
cover_letter_template = ""

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

def get_docx_text(docx_path):

    full_text = []

    scan_docx(docx_path, lambda s: full_text.append(s))

    return full_text

def get_templates():
    global paths
    global resume_template
    global json_template
    global cover_letter_template
    global resume_prompt

    prompt_path = paths['resources'] / "Resume Prompt.md"
    json_path = paths['resources'] / "Json Template.json"
    resume_template = paths['resources'] / "Resume Template.docx"
    cover_letter_template = paths['resources'] / "Cover Letter Template.docx"

    with open(json_path, "r", encoding="utf-8") as file:
        json_template = json.load(file)
    
    with open(prompt_path, 'r', encoding="utf-8") as file:
        resume_prompt = file.read()

def get_json_datas():
    global paths
    json_datas = []
    ensure_path_exists(paths["json_data"])

    json_paths = list(paths['json_data'].glob("*.json"))
    
    for path in json_paths:
        with open(path, 'r', encoding="utf-8") as file:
            json_datas.append(json.load(file))

    return json_datas

def save_document_result(doc: Document, name: str):
    global paths

    full_path = paths["results"] / f'{name}.docx'

    doc.save(full_path)

def save_document_temp(doc: Document, name: str):
    global paths

    ensure_path_exists(paths['temp'])

    full_path = paths['temp'] / f'{name}.docx'

    doc.save(full_path)

def clear_temp():
    global paths
    temp_path = paths['temp']

    for file in Path(temp_path).glob("*"):
        if file.is_file():
            file.unlink()

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

    for resume in base_resumes:
        full_base_resume_text += f"\n{'-'*50}\n{resume.name}\n {'-'*50}\n"
        text = get_docx_text(resume)
        base_resume_texts.append('\n'.join(text))
        full_base_resume_text += "\n".join(text)

    return full_base_resume_text
#endregion

#region Main Script

get_base_resumes()
get_templates()
get_resume_full_resume_text()

# Populate base resume texts

#endregion

get_json_datas()