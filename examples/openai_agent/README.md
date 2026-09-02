# Promas with OpenAI API

This example demonstrates how to integrate Promas into **OpenAI Chat Completions** or the **OpenAI Assistants API** using native Function / Tool Calling.

---

## 1. Quick Test

Set your API key and run the script:
```bash
export OPENAI_API_KEY="your-key"
python examples/openai_agent/openai_promas_tool.py
```

---

## 2. Integration Pattern

1. Register `PROMAS_TOOL_SCHEMA` inside the `tools` array when making a chat completion request.
2. When OpenAI requests a tool call for `fetch_product_images`, invoke Promas via `asyncio.run(get_product_images(...))`.
3. Feed the JSON result back as a `tool` role message so the model can answer with grounded product imagery.
