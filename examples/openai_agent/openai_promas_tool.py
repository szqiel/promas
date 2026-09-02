"""
Example: OpenAI Function / Tool Calling with Promas
Demonstrates native OpenAI Chat Completions tool-calling using Promas for visual verification.
"""

import asyncio
import json
import os

from openai import OpenAI

from promas import get_product_images

# Define the Tool Definition Schema for OpenAI API
PROMAS_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_product_images",
        "description": "Universally extracts verified high-resolution product photography and official links.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The product name, model identifier, or direct e-commerce product URL."
                },
                "max_images": {
                    "type": "integer",
                    "description": "Maximum number of verified high-res images to return.",
                    "default": 5
                },
                "site_filter": {
                    "type": "string",
                    "description": "Optional domain filter (e.g. 'apple.com', 'nike.com')."
                }
            },
            "required": ["query"]
        }
    }
}


async def execute_promas_tool(arguments_json: str) -> str:
    args = json.loads(arguments_json)
    result = await get_product_images(
        query=args.get("query"),
        max_images=args.get("max_images", 5),
        site_filter=args.get("site_filter")
    )
    return result.model_dump_json()


def run_openai_agent_demo():
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "mock-key-for-syntax-check"))

    messages = [
        {"role": "system", "content": "You are a helpful product shopping assistant. Use fetch_product_images when requested."},
        {"role": "user", "content": "Show me official photos for the Nike Air Jordan 1."}
    ]

    print("[*] Sending request to OpenAI API with Promas Tool Schema...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=[PROMAS_TOOL_SCHEMA],
            tool_choice="auto"
        )

        message = response.choices[0].message
        if message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.function.name == "fetch_product_images":
                    print(f"[*] OpenAI called tool with args: {tool_call.function.arguments}")
                    tool_output = asyncio.run(execute_promas_tool(tool_call.function.arguments))
                    print("[*] Promas Returned Output:")
                    print(tool_output)
    except Exception as e:
        print(f"[!] OpenAI API Notice (Set OPENAI_API_KEY to test live): {e}")


if __name__ == "__main__":
    run_openai_agent_demo()
