from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from icecream import ic
import json
import os

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Create OpenAI client
client = OpenAI()

model = "gpt-5"
role = "user"

# Extract the main message content


def create_request(message):
    global model
    global role

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": role, "content": message}
        ]
    )

    message_content = response.choices[0].message.content

    return message_content
