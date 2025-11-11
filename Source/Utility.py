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
    "json_data" : base_dir / "Resources" / "Json Data"
}

base_resumes = []
base_resume_texts = []
full_base_resume_text = ""


json_template = {}
resume_template = ""

#endregion

#region Functions

def get_base_resumes():
    global paths
    global base_resumes

    folder = Path(paths["base_resume"])
    ensure_path_exists(folder)

    base_resumes = [f for f in folder.glob("*.docx") if not f.name.startswith("~$")]

def get_docx_text(docx_path):

    full_text = []
    doc = Document(docx_path)

    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                full_text.append(cell.text)

    for section in doc.sections:
        for paragraph in section.header.paragraphs:
            if paragraph.text.strip():
                full_text.append(paragraph.text)

        for paragraph in section.footer.paragraphs:
            if paragraph.text.strip():
                full_text.append(paragraph.text)

    return full_text

def get_templates():
    global paths
    global resume_template
    global json_template

    json_path = paths['resources'] / "Json Template.json"
    resume_template = paths['resources'] / "Resume Template.docx"

    with open(json_path, "r", encoding="utf-8") as file:
        json_template = json.load(file)

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

def replace_keys(dict_obj, modifier):
    result = {}

    for key, value in dict_obj.items():
        new_key = modifier(key)
        result[new_key] = value

    return result
#endregion

#region Main Script

get_base_resumes()
get_templates()

# Populate base resume texts
for resume in base_resumes:
    full_base_resume_text += f"\n{'-'*50}\n{resume.name}\n {'-'*50}\n"
    text = get_docx_text(resume)
    base_resume_texts.append('\n'.join(text))
    full_base_resume_text += "\n".join(text)


#endregion