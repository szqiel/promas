# Promas (Product Image Scraper)

[![PyPI version](https://img.shields.io/pypi/v/promas.svg)](https://pypi.org/project/promas/)
[![CI](https://github.com/szqiel/promas/actions/workflows/ci.yml/badge.svg)](https://github.com/szqiel/promas/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://modelcontextprotocol.io/)

**Promas** is an automated product image scraper and Model Context Protocol (MCP) server for AI agents.

Instead of writing fragile per-site scrapers that break whenever HTML structures change, Promas combines **Pluggable Search-Driven Discovery** with a **Universal Semantic Extraction Pipeline** and **Extensible CDN-Aware Upscaling**. It reliably extracts master-resolution product photography across any brand or retail site (Apple, Nike, Sony, Amazon, Target, B&H, Best Buy, eBay, Shopify stores, and arbitrary product URLs).

---

## 1. Quickstart

### Option A: Install from PyPI (Recommended)
```bash
pip install promas
playwright install chromium
```

Run instantly from anywhere:
```bash
promas "iPhone 16 Pro"
```

### Option B: Run with Docker (Zero local Python / Playwright setup)
```bash
# Build the Docker image
docker build -t promas .

# Run the FastMCP Server for your AI Agent
docker run -i --rm promas

# Or run the standalone CLI scraper
docker run --rm promas promas "Sony FX3"
```

---

## 2. Why Promas? (Comparison)

| Feature | Raw Scripts (`BeautifulSoup`, `Puppeteer`) | Paid APIs (`Bright Data`, `ScrapingBee`) | **Promas** |
| :--- | :--- | :--- | :--- |
| **Cost** | Free | \$50–\$500+/mo recurring | **100% Free & Open-Source (MIT)** |
| **Setup & Maintenance** | Fragile per-site selectors; breaks on redesigns | Generic HTML responses; requires custom parsers | **Search-Driven + Semantic Schemas + CDN Upscalers** |
| **Anti-Bot & Rate Limits** | Blocked quickly by Cloudflare/Akamai | Handled in cloud | **Per-Domain Rate Limiter + Stealth + Tenacity Retries** |
| **Image Verification** | None; returns broken links & 1x1 pixels | Basic status check | **Async HTTP validation + pHash perceptual dedup** |
| **Search Backends** | Hardcoded scrapers | Custom API scrapers | **Pluggable (Brave API / SerpAPI / Browser Fallback)** |
| **Caching** | None | Extra cost | **Built-in TTL Disk Cache (Sub-second repeated queries)** |
| **Image Quality** | Usually captures low-res UI thumbnails | Raw page images only | **Master CDN de-capping (up to 2500px+)** |
| **AI Agent Native** | Manual wrapper needed | REST API only | **Native FastMCP Tool Protocol + Docker support** |

---

## 3. Key Features

- **Pluggable Search Backends**:
  - **Primary (Official APIs)**: Supports **Brave Search API** (`BRAVE_API_KEY`) and **SerpAPI** (`SERPAPI_API_KEY`) for fast, stable, ToS-compliant query discovery.
  - **Fallback (Browser-based)**: Built-in Playwright Stealth discovery queries Bing and DuckDuckGo when no API keys are configured.
- **Universal Semantic Extraction**: Extracts imagery across Schema.org JSON-LD (`Product`, `IndividualProduct`, `ItemPage`), Microdata (`[itemprop="image"]`), OpenGraph (`og:image`), Twitter Cards, and responsive `srcset` attributes.
- **Extensible CDN-Aware Upscaling**: Plugin-based `@register_cdn` registry unwraps thumbnail restrictions and upsamples to master resolutions across **Adobe Scene7, Nike CDN, Shopify, Amazon CloudFront, Imgix, Cloudinary, Akamai, eBay, and B&H**.
- **Lightweight Async Verification**: Validates image MIME types (`image/*`), content-length, and actual pixel dimensions before returning results.
- **Perceptual-Hash Deduplication (`imagehash`)**: Detects and eliminates near-identical photo crops/angles across different sources, keeping only the highest-resolution master asset.
- **Per-Domain Rate Limiting & Concurrency**: Restricts simultaneous connections per domain with polite inter-request delays to protect target servers and prevent IP bans.
- **Tenacity Retries with Exponential Backoff**: Automatically recovers from transient network drops and navigation timeouts.
- **TTL Disk Caching**: Keyed on normalized query and filter parameters; eliminates redundant re-scraping with sub-second response times.
- **Structured Logging (`loguru`)**: Full observability with detailed debug tracing for DOM selectors, schema blocks, cache hits, and warnings on failed page attempts.
- **FastMCP Protocol**: Plugs natively into AI Agent workflows (Antigravity, Claude Desktop, Cursor, OpenAI Agents).

---

## 4. Usage

### A. Standalone CLI

#### Search by Product Name:
```bash
promas "iPhone 16 Pro"
```

#### Extract from a Direct URL:
```bash
promas "https://www.apple.com/iphone-16-pro/"
```

#### Filter by Specific Domain & Limit Count:
```bash
promas "Sony FX3" --max-images 5 --site bhphotovideo.com
```

#### Bypass Cache or Disable Verification:
```bash
promas "Nike Air Jordan 1" --no-cache --no-verify
```

### B. FastMCP Server
Run the standalone MCP server:
```bash
promas-mcp
```

### C. Agent Integration (`mcp_config.json`)

#### Native Python Installation:
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

#### Docker Container (Zero-dependency setup):
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

## 5. Agent System Prompt Guidelines

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

## 6. Output Schema

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

---

## 7. Testing & Quality Assurance

Promas includes unit tests for pure parsing functions, type checks, and canary integration tests:

```bash
# Run unit tests
pytest -v

# Run linting
ruff check .

# Run type checker
mypy promas/ tests/

# Run live golden canary integration tests (hits live sites)
pytest -v --run-integration
```

---

## 8. License

This project is licensed under the [MIT License](LICENSE).
