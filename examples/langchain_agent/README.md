# Promas with LangChain

This example demonstrates how to integrate Promas into **LangChain** agents using the `@tool` decorator or LangChain MCP adapters.

---

## 1. Quick Test

Run the example script directly:
```bash
python examples/langchain_agent/langchain_promas.py
```

---

## 2. Using with an LLM Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from examples.langchain_agent.langchain_promas import fetch_product_images_tool

# Initialize tools and model
tools = [fetch_product_images_tool]
llm = ChatOpenAI(model="gpt-4o", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an e-commerce assistant. Use fetch_product_images_tool to retrieve verified product photos."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run agent
response = agent_executor.invoke({"input": "Find high-res images for the iPhone 16 Pro"})
print(response["output"])
```
