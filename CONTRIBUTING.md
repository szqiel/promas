# Contributing to Promas

Thank you for your interest in contributing to Promas! 🎉

Promas is designed with a **plugin-based, decentralized CDN architecture**. Adding master resolution upscaling for a new e-commerce platform or CDN takes **less than 10 lines of code** and can be submitted as an easy Pull Request.

---

## 🚀 How to Add a New CDN / Store Rule (in 3 Steps)

### Step 1: Create a new file in `promas/cdn/`
Name your file after the retailer or CDN provider (e.g. `promas/cdn/my_store.py`).

### Step 2: Implement and decorate your normalizer function
Use the `@register_cdn("<domain>")` decorator. Your function receives a raw image URL and returns the upscaled master resolution URL:

```python
"""
MyStore CDN Normalizer Rule
"""
import re
from promas.cdn.registry import register_cdn

@register_cdn("images.mystore.com")
@register_cdn("cdn.mystore.net")
def upscale_mystore(url: str) -> str:
    """
    Transforms thumbnail dimensions (e.g. _300x300.jpg) to master asset resolution.
    """
    # Example: Upgrade 300x300 to 2000x2000 master
    return re.sub(r'_\d+x\d+\.', '_2000x2000.', url)
```

### Step 3: Register in `promas/cdn/__init__.py`
Add one line to import your module so it registers automatically:

```python
import promas.cdn.my_store
```

That's it! Your rule is now live and automatically applied whenever Promas encounters images from that domain.

---

## 🧪 Testing Your CDN Rule

You can test your rule with a quick Python one-liner:

```bash
python -c "from promas.cdn import clean_and_upscale_image_url; print(clean_and_upscale_image_url('https://images.mystore.com/item_300x300.jpg'))"
```

Or run an end-to-end CLI scrape:

```bash
python promas.py "Product Name on MyStore"
```

---

## 🛠️ Submitting a Pull Request

1. **Fork the repository** on GitHub.
2. **Create a branch**: `git checkout -b feature/add-mystore-cdn`
3. **Commit your changes**: `git commit -m "feat(cdn): add upscale rule for MyStore"`
4. **Push to GitHub**: `git push origin feature/add-mystore-cdn`
5. **Open a Pull Request** describing the store and an example upscaled image URL!

---

## 💡 Other Ways to Contribute

- **Search Backends**: Add alternative search backends in `promas/search_backends/`.
- **Extractor Enhancements**: Improve Schema.org / Microdata edge-case handling in `promas/core/extractor.py`.
- **Bug Reports & Ideas**: Open an issue on GitHub!
