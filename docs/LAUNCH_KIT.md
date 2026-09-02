# Promas Launch Kit & Community Distribution

This guide provides copy-pasteable launch posts, threads, and pitch angles for distributing **Promas** across Reddit, X (Twitter), Hacker News, and AI Developer Discords.

---

## 1. Reddit Post Draft

**Target Subreddits**:
- `r/ClaudeAI`
- `r/LocalLLaMA`
- `r/OpenAI`
- `r/LangChain`
- `r/webscraping`

### Post Title:
> **I built Promas: An open-source MCP server that gives AI agents verified, master-resolution product photography (No hallucinated URLs)**

### Post Body:
```markdown
Hey everyone! 👋

One of the most frustrating things when building shopping assistants or research agents is visual hallucination — LLMs will happily invent dead image URLs or pull blurry 1x1 tracking pixels when asked for product photos.

To solve this, I built **Promas (Product Image Scraper)** — a 100% open-source FastMCP server and CLI designed specifically for AI agents:

👉 **GitHub**: https://github.com/szqiel/promas

### 💡 How it works under the hood:
1. **Search-Driven Discovery**: No hardcoded store search URLs. Accepts `"iPhone 16 Pro"`, `"Sony FX3"`, or direct URLs, and dynamically scores authoritative retailers across Brave Search API / SerpAPI or built-in stealth browser discovery.
2. **Universal Semantic Extraction**: Extracts imagery across Schema.org JSON-LD, Microdata (`[itemprop="image"]`), OpenGraph, and responsive DOM `srcset`.
3. **CDN Master Upscaling**: De-caps thumbnail restrictions to return master resolutions (up to 2500px+) across Adobe Scene7, Nike CDN, Shopify, Amazon CloudFront, Imgix, and B&H.
4. **Perceptual-Hash Deduplication (`imagehash`)**: Detects near-identical photo crops across different sources and automatically keeps the highest-resolution version.
5. **Polite & Resilient**: Features per-domain rate limiting, tenacity retries, and TTL disk caching (<0.1s repeat queries).

### 🚀 Quickstart:

```bash
pip install promas
promas "iPhone 16 Pro"
```

Or connect it to **Claude Desktop / Cursor** via MCP (`promas-mcp` or Docker `docker run -i --rm promas`).

Check out the repo, try it on your favorite products, and let me know what CDN rules or features you'd like added! Feedback and contributions are warmly welcome!
```

---

## 2. X (Twitter) Launch Thread

**Media to Attach**: `docs/assets/demo.gif`

### Tweet 1 (Hook):
> LLMs are great at text, but they constantly hallucinate product images with dead links or tiny tracking pixels.
>
> Built **Promas** — an open-source MCP server for AI agents that extracts verified, master-res product photography across any retailer 🛍️📸
>
> 🧵👇 (Demo below)

### Tweet 2 (Features):
> Instead of brittle per-site scrapers:
> 🔍 Pluggable search discovery (Brave / SerpAPI / Stealth)
> 🧬 Universal Schema.org JSON-LD & OG extraction
> 🚀 CDN upscalers (Scene7, Nike, Shopify, Amazon)
> 🧮 pHash perceptual deduplication (drops near-identical crops)

### Tweet 3 (CTA & Links):
> Works natively with Claude Desktop, Cursor, LangChain, and OpenAI Agents.
>
> 📦 PyPI: `pip install promas`
> 🐳 Docker: `docker run -i --rm promas`
> ⭐ GitHub: https://github.com/szqiel/promas

---

## 3. Hacker News (Show HN)

### Title:
> **Show HN: Promas – Universal product image scraper and MCP server for AI agents**

### Body:
```text
Hey HN,

I built Promas (https://github.com/szqiel/promas), an open-source FastMCP server and CLI in Python that provides verified, master-resolution product photography for AI agents and developers.

The Core Problem:
Language models have no native visual grounding for physical products. When an agent is asked for product packshots or colorways, it often invents URLs or returns low-resolution thumbnail fragments.

Architecture:
- Discovery: Combines ToS-compliant search backends (Brave / SerpAPI) with Playwright stealth browser fallback.
- Extraction: Parses Schema.org JSON-LD (`Product`, `ItemPage`), Microdata, OpenGraph, and srcset.
- CDN Normalization: Plugin registry that unwraps dynamic image transformations on Adobe Scene7, Shopify, Amazon CloudFront, Nike, and Imgix to fetch 2000px+ master photography.
- Quality Pipeline: Async HTTP MIME & pixel dimension validation + perceptual hashing (`imagehash.phash`) to eliminate duplicate crops across multiple retailer scrapes.
- Caching & Concurrency: Built-in TTL disk caching and per-domain rate limiting.

Feedback and contributions for new CDN rules are very welcome!
```

---

## 4. Discord Snippet (Anthropic / Cursor / MCP Discords)

```text
Hey everyone! Just open-sourced **Promas** — an MCP server that gives AI agents verified, high-resolution product photography without URL hallucinations:
https://github.com/szqiel/promas

Works out of the box with Claude Desktop, Cursor, and Python agents (`pip install promas`). Check it out if you're building shopping assistants or e-commerce agent workflows!
```
