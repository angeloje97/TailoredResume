from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from pathlib import Path
from Utility import get_config
from icecream import ic
import json
import os

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Create async clients
openai_client = AsyncOpenAI()
anthropic_client = AsyncAnthropic()

role = "user"

# Extract the main message content


async def create_gpt_request(model, message):
    response = await openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": role, "content": message}
        ]
    )
    return response.choices[0].message.content


def strip_markdown_code_fence(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()


async def create_claude_request(model, message):
    response = await anthropic_client.messages.create(
        model=model,
        max_tokens=16000,
        messages=[
            {"role": role, "content": message}
        ]
    )
    message_content = next(
        (block.text for block in response.content if block.type == "text"), ""
    )
    return strip_markdown_code_fence(message_content)


async def create_request(message):
    config = get_config()
    model = config['Settings']['Current Model']

    if "claude" in model:
        return await create_claude_request(model, message)
    elif "gpt" in model:
        return await create_gpt_request(model, message)
