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


async def create_gpt_request(model, message, on_chunk=None):
    if on_chunk is None:
        response = await openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": role, "content": message}
            ]
        )
        content = response.choices[0].message.content
        if not content:
            ic(response.choices[0].finish_reason, response.usage, response)
        return content

    content_parts = []
    finish_reason = None
    stream = await openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": role, "content": message}
        ],
        stream=True
    )
    async for event in stream:
        choice = event.choices[0]
        if choice.finish_reason:
            finish_reason = choice.finish_reason
        delta = choice.delta.content
        if delta:
            content_parts.append(delta)
            on_chunk(delta)

    content = "".join(content_parts)
    if not content:
        ic(finish_reason)
    return content


def strip_markdown_code_fence(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()


async def create_claude_request(model, message, on_chunk=None):
    anthropic_settings = get_config()['Settings'].get('Anthropic', {})
    thinking_type = anthropic_settings.get('Thinking Type', 'adaptive')
    effort = anthropic_settings.get('Effort', 'medium')

    async with anthropic_client.messages.stream(
        model=model,
        max_tokens=32000,
        thinking={"type": thinking_type},
        output_config={"effort": effort},
        messages=[
            {"role": role, "content": message}
        ]
    ) as stream:
        if on_chunk is not None:
            async for text in stream.text_stream:
                on_chunk(text)
        response = await stream.get_final_message()

    message_content = next(
        (block.text for block in response.content if block.type == "text"), ""
    )
    if not message_content:
        ic(response.stop_reason, response.usage, response.content)
    return strip_markdown_code_fence(message_content)


async def create_request(message, on_chunk=None):
    config = get_config()
    model = config['Settings']['Current Model']

    if "claude" in model:
        return await create_claude_request(model, message, on_chunk)
    elif "gpt" in model:
        return await create_gpt_request(model, message, on_chunk)
