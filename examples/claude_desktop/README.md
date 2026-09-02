# Promas on Claude Desktop

This guide explains how to connect Promas to **Claude Desktop** to give Claude real-time visual grounding for physical products.

---

## 1. Prerequisites

Make sure you have installed `promas`:
```bash
pip install promas
playwright install chromium
```
*(Or build the Docker image if you prefer zero local Python dependencies)*

---

## 2. Configuration File Locations

Open your Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

---

## 3. Configuration Setup

### Option A: Local Python / Pip Binary (Recommended)

```json
{
  "mcpServers": {
    "promas": {
      "command": "promas-mcp",
      "env": {
        "BRAVE_API_KEY": "optional-key-here"
      }
    }
  }
}
```

### Option B: Docker Container (Zero local Playwright/Python install)

```json
{
  "mcpServers": {
    "promas": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "promas"]
    }
  }
}
```

---

## 4. How to Test with Claude

1. Restart Claude Desktop.
2. Look for the **🔌 Tool hammer icon** in the prompt box to verify `promas` tools are loaded (`fetch_product_images`, `search_product_urls`, `scrape_single_url`).
3. Ask Claude:
   > *"Can you fetch official high-resolution photos and colorways for the Sony FX3 Cinema Camera?"*
4. Claude will automatically trigger Promas, verify the CDN images, and display them inline in Markdown!
