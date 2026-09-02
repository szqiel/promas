# MCP Registry Submissions & Directory Listings

This document contains pre-formatted submission snippets, PR templates, and directory metadata to register **Promas** on all major Model Context Protocol (MCP) registries and ecosystem lists.

---

## 1. Awesome MCP Servers (`punkpeye/awesome-mcp-servers`)

- **Repository**: [https://github.com/punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- **Target Category**: *Search / Scraping / E-commerce* or *Media / Images*

### Markdown Entry to Add to `README.md`:
```markdown
- [Promas](https://github.com/szqiel/promas) - Universal product image scraper and MCP server for AI agents. Extracts verified master-resolution photography across Apple, Nike, Sony, Amazon, Target, and arbitrary e-commerce URLs with perceptual deduplication and CDN upscaling.
```

### Pull Request Title:
`Add Promas - Universal Product Image Scraper and MCP Server`

### Pull Request Description:
```markdown
### Summary
Added **Promas** ([szqiel/promas](https://github.com/szqiel/promas)) to the list of MCP servers under E-Commerce / Search / Media.

### What is Promas?
Promas is an open-source MCP server and CLI that solves AI agent visual hallucination for physical products. It combines search-driven discovery with Schema.org JSON-LD extraction, CDN master upscaling (Adobe Scene7, Nike, Shopify, Amazon), and perceptual-hash deduplication (`imagehash`).

### Tool Capabilities
- `fetch_product_images`: Full automated pipeline from query/URL to verified master image links.
- `search_product_urls`: Fast discovery of candidate retail pages.
- `scrape_single_url`: Direct page extraction for a specific product URL.
```

---

## 2. Smithery Registry (`smithery.ai`)

Promas includes `smithery.yaml` in the root of the repository.

### Install Command for Users:
```bash
npx -y @smithery/cli install promas --client claude
```

### How to Index:
1. Visit [https://smithery.ai/new](https://smithery.ai/new)
2. Enter repository URL: `https://github.com/szqiel/promas`
3. Click **Import Repository**. Smithery will automatically parse `smithery.yaml` and publish the listing.

---

## 3. Official Anthropic MCP Community Servers

- **Repository**: [https://github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)

### Description:
```markdown
### Promas
- Repository: https://github.com/szqiel/promas
- License: MIT
- Description: Universal product image scraper and FastMCP server for AI agents. Extracts high-resolution master photography from any brand, retailer, or direct URL.
```

---

## 4. Other MCP Hubs & Directories

- **Glama (glama.ai/mcp/servers)**: Submit via GitHub OAuth at `glama.ai/mcp`.
- **MCP.so / Pulse MCP**: Submit repository URL `https://github.com/szqiel/promas`.
