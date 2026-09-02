# Promas on Cursor IDE

This guide shows how to integrate Promas into **Cursor IDE** so Cursor Composer & Agent can inspect and extract product assets while you build web or mobile apps.

---

## 1. Setup in Cursor

1. Open **Cursor Settings** (`Cmd + ,` or `Ctrl + ,`).
2. Navigate to **Features** ➔ **MCP Servers** ➔ **Add New MCP Server**.
3. Fill in the fields:
   - **Name**: `promas`
   - **Type**: `command` (or `stdio`)
   - **Command**: `promas-mcp` (or `python -m promas.server.mcp_server`)

---

## 2. Or Configure via JSON

You can configure MCP servers directly in your project root at `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "promas": {
      "command": "promas-mcp",
      "env": {
        "BRAVE_API_KEY": ""
      }
    }
  }
}
```

---

## 3. Example Use Cases in Cursor

- **E-Commerce Mockups**:
  > *"Cursor, create a product detail page component for 'Nike Air Jordan 1' and use Promas to fetch official master image assets for the gallery."*
- **Catalog Population**:
  > *"Fetch official high-res images for 'Sony A7 IV' and generate an assets JSON fixture for our unit tests."*
