from pathlib import Path
from icecream import ic
from docx import Document
import json


#region Global Variables

base_dir = Path(__file__).parent.parent

paths = {
    "base_resume": base_dir / "BaseResumes",
    "resources": base_dir / "Resources",
    "results": base_dir / "Results"
}

base_resumes = []
base_resume_texts = []

json_template = {}
resume_template = ""

#endregion

#region Functions

def get_base_resumes():
    global paths
    global base_resumes

    folder = Path(paths["base_resume"])
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

    return full_text



def get_templates():
    global paths
    global resume_template
    global json_template

    json_path = paths['resources'] / "Json Template.json"
    resume_template = paths['resources'] / "Resume Template.docx"

    with open(json_path, "r", encoding="utf-8") as file:
        json_template = json.load(file)

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
    text = get_docx_text(resume)
    base_resume_texts.append('\n'.join(text))
    ic(base_resume_texts)

#endregion