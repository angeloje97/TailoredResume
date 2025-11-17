from openai import AsyncOpenAI
from dotenv import load_dotenv
from pathlib import Path
from Utility import get_config
from icecream import ic
import json
import os

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Create async OpenAI client
client = AsyncOpenAI()

role = "user"

# Extract the main message content


async def create_request(message):
    global role

    config = get_config()

    # response = await client.responses.create(
    #     model=model,
    #     input=message
    # )
    response = await client.chat.completions.create(
        model=config['Settings']['GPT Model'],
        messages=[
            {"role": role, "content": message}
        ]
    )

    # message_content = response.output_text
    message_content = response.choices[0].message.content
    return message_content
