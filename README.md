# Promas (Product Image Scraper)

Promas is an extensible, automated product image scraper and Model Context Protocol (MCP) server for AI agents. It uses **Playwright Async + Stealth** and **JSON-LD Schema.org** parsing to bypass anti-bot WAF protections and extract master high-resolution CDN images across e-commerce platforms.

---

## 1. Features

- **Anti-Bot Stealth**: Randomizes browser fingerprints, suppresses automation headers, and bypasses Akamai/Cloudflare challenges via `playwright-stealth`.
- **Master CDN Image Extraction**: Bypasses DOM zoom/gallery hydration by parsing `<script type="application/ld+json">` metadata directly.
- **FastMCP Protocol Support**: Easily connect to AI agents (Antigravity, Claude Desktop, Cursor, etc.).
- **Multi-Source Ready**: Modular source routing (`source="bh"`, expandable to Adorama, Amazon, BestBuy, etc.).
- **Standalone CLI**: Can be run directly via command-line or imported as a Python module.

---

## 2. Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Chromium Browser:**
   ```bash
   playwright install chromium
   ```

---

## 3. Usage

### A. Standalone CLI
Run a direct query from the command line:
```bash
python promas.py "Sony FX3"
```
Or specify a source:
```bash
python promas.py "Godox TT600" --source bh
```

### B. FastMCP Server
Run the MCP server:
```bash
python promas_mcp_server.py
```

### C. Agent Integration (`mcp_config.json`)
Add Promas to your agent configuration:
```json
{
  "mcpServers": {
    "promas": {
      "command": "python",
      "args": ["c:/Users/SYAIR/Documents/Project/promas/promas_mcp_server.py"]
    }
  }
}
```

---

## 4. Agent System Prompt Guidelines

Add the following instructions to your AI agent's system prompt:

```text
You have access to the `get_product_images` tool (Promas), which queries e-commerce platforms (such as B&H Photo) to find high-resolution product imagery and official product links.

GUIDELINES FOR USING PROMAS:
1. When asked for product images or visual references, call `get_product_images(query=<specific product name and model>, source="bh")`.
2. Do not invent or guess image URLs; strictly return the URLs provided by the tool.
3. Present the primary high-res image as markdown (e.g. `![Product Image](url)`) and provide additional gallery links or the product page link if relevant.
4. If status is 'error', politely notify the user and verify the search term.
```

---

## 5. Output Schema

```json
{
  "status": "success",
  "source": "bh",
  "query": "Sony FX3",
  "title": "Sony FX3 Full-Frame Cinema Camera",
  "product_url": "https://www.bhphotovideo.com/c/product/1628875-REG/sony_ilme_fx3_fx3_cinema_camera.html",
  "images": [
    "https://static.bhphoto.com/images/images500x500/1614138379_1628875.jpg",
    "https://static.bhphoto.com/images/multiple_images/images500x500/1614138380_IMG_1502476.jpg"
  ],
  "error_message": null
}
```
