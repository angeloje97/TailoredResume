from Utility import paths, write_to_docx, get_json_datas, expand_list_to_keys, replace_keys, resume_template, cover_letter_template, save_document_result
from icecream import ic

json_datas = get_json_datas()

for data in json_datas:
    resume_data = data['Resume']
    
    cover_letter_data = data['CoverLetter']

    resume_data = expand_list_to_keys(resume_data, "")

    resume_doc = write_to_docx(resume_template, resume_data)

    cover_letter_doc = write_to_docx(cover_letter_template, cover_letter_data)

    resume_name = resume_data['File Name']
    cover_letter_name = cover_letter_data['File Name']

    save_document_result(resume_doc, resume_name)
    save_document_result(cover_letter_doc, cover_letter_name)