# Promas (Product Image Scraper)

**Promas** is a scalable, zero-hardcoding product image scraper and Model Context Protocol (MCP) server for AI agents.

Unlike traditional scrapers that rely on fragile per-site CSS selectors, Promas uses a **Search-Driven Dynamic Discovery + Universal Semantic Extraction Pipeline** with Playwright Stealth, Schema.org JSON-LD parsing, OpenGraph/Microdata discovery, and master CDN upscalers. It works across **any brand or e-commerce platform** on the web (Apple, Nike, Sony, Amazon, Target, B&H, Best Buy, eBay, Shopify stores, and arbitrary product URLs).

---

## 1. Key Features

- **Zero-Hardcoding Universal Architecture**: Scrapes any brand, retailer, or custom e-commerce store without requiring custom per-site scraper code.
- **Search-Driven Dynamic Discovery**: Given any product query (e.g. `"iPhone 16 Pro"`, `"Nike Air Jordan 1"`), dynamically finds and visits authoritative product pages.
- **Multi-URL Parallel Redundancy**: Scrapes top candidate product pages concurrently via `asyncio.Semaphore` so individual site blocks or timeouts never stall the pipeline.
- **Universal Semantic Extraction**: Extracts imagery across Schema.org JSON-LD (`Product`, `IndividualProduct`, `ItemPage`), Microdata (`itemprop="image"`), OpenGraph (`og:image`), Twitter Cards, and responsive `srcset` / high-res `data-*` attributes.
- **Master CDN Upscaler**: Strips thumbnail size bounds and upscales resolutions across Cloudflare, Shopify, Amazon CloudFront, Scene7, Imgix, Akamai, eBay, and B&H.
- **Direct Image Index Fallback**: Automatically queries high-resolution open image search if candidate web pages are unreachable.
- **Direct URL Support**: Pass any direct product URL (e.g. `https://www.apple.com/iphone-16-pro/`) to scrape it immediately.
- **FastMCP Protocol**: Connects directly to AI Agents (Antigravity, Claude Desktop, Cursor, OpenAI Agents).

---

## 2. Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Chromium:**
   ```bash
   playwright install chromium
   ```

---

## 3. Usage

### A. Standalone CLI

#### Search by Product Name:
```bash
python promas.py "iPhone 16 Pro"
```

#### Extract from a Direct URL:
```bash
python promas.py "https://www.apple.com/iphone-16-pro/"
```

#### Customize Image Count & Filter by Site:
```bash
python promas.py "Sony FX3" --max-images 5 --site bhphotovideo.com
```

### B. FastMCP Server
Run the MCP server:
```bash
python promas_mcp_server.py
```

### C. Agent Integration (`mcp_config.json`)
Add Promas to your agent or Claude Desktop configuration:
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
You have access to the `fetch_product_images` tool (Promas), which universally retrieves high-resolution product imagery and official product links from across the web.

GUIDELINES FOR USING PROMAS:
1. When asked for product images, photos, or visual references, call `fetch_product_images(query=<specific product name or direct URL>)`.
2. Do not invent or hallucinate image URLs; strictly return the verified URLs returned by Promas.
3. Render primary high-res images as markdown (e.g. `![Product Photo](url)`) and provide source product links for reference.
4. If a specific store is desired by the user, you can supply `site_filter` (e.g. `site_filter="apple.com"`).
```

---

## 5. Output Schema

```json
{
  "status": "success",
  "query": "iPhone 16 Pro",
  "title": "Apple iPhone 16 Pro",
  "sources_scraped": [
    "https://www.target.com/p/apple-iphone-16-pro/-/A-93597960",
    "https://www.amazon.com/Apple-iPhone-Version-256GB-Titanium/dp/B0DHJDPYYR",
    "https://www.apple.com/shop/buy-iphone/iphone-16"
  ],
  "images": [
    "https://target.scene7.com/is/image/Target/GUEST_7c0750b4-ee18-41d4-9309-d08e41619229",
    "https://target.scene7.com/is/image/Target/GUEST_4e1ce623-313f-4193-93a4-61dc0fc9da14"
  ],
  "error_message": null
}
```
