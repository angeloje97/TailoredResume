from Utility import paths, write_to_docx, get_json_datas, expand_list_to_keys, replace_keys, resume_template, save_resume
from icecream import ic

json_datas = [expand_list_to_keys(item, " ") for item in get_json_datas()]

for index, data in enumerate(json_datas):
    new_doc = write_to_docx(resume_template, data)
    
    if 'Meta' in data:
        meta = data['Meta']
        name = meta['File Name']

        save_resume(new_doc, f"{name}")
