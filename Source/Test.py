from Utility import paths, write_to_docx, get_json_datas, expand_list_to_keys, replace_keys, resume_template, cover_letter_template, save_document_result, scan_docx, save_document_temp
from Agent import create_request
from icecream import ic
import asyncio
import json

# Example: Get text from resume template
text = []
scan_docx(resume_template, lambda s: text.append(s))
text = "".join(text)

# How to call the async create_request function in a non-async context:
# Create and run an event loop to execute the async function

message = f"Give me a response in JSON format from this text. The keys are surrounded by brackets" 
message += "\nIf it's not surrounded by brackets don't make it a key. Also come up with the values for each key and pretend you are a software engineer applying to a tech job for AI specialization."
message += "Also don't include the brackets. {example} = example"
message += "There are 32 available lines and each line can contain 85 characters. Try your best not to overflow and make a 2nd page for the word document."
message += "But also try to fill the text out so that it could reach close to a full page. Just not more than 1 page"
message += f"\n{text}\n"

# Method 1: Using asyncio.run() (Python 3.7+, simplest approach)
response = asyncio.run(create_request(message))

data = json.loads(response)

new_doc = write_to_docx(resume_template, data)

save_document_temp(new_doc, "Mock Resume")

# Method 2: Manual event loop management (used in Main.py's AIWorker)
# This is useful when you need more control over the event loop
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# response2 = loop.run_until_complete(create_request(message))
# loop.close()
# ic(response2)