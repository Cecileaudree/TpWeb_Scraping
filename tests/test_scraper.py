from __future__ import annotations

import json
from pathlib import Path

from bs4 import BeautifulSoup

from src.extraction import extract_items
from src.normalization import normalize_item, normalize_items


def load_sample_html() -> str:
    path = Path(__file__).resolve().parent.parent / "samples" / "sample_page.html"
    return path.read_text(encoding="utf-8")


def test_extract_items_count():
    html = load_sample_html()
    items = extract_items(
        html,
        "samples/sample_page.html",
        ".product-card",
        {
            "title": ".product-title",
            "price": ".product-price",
            "link": ".product-link",
            "availability": ".product-availability",
            "published_date": "time",
        },
    )
    assert len(items) == 3


def test_normalize_price_and_date():
    raw = {
        "title": "Produit A",
        "price": "€ 19,90",
        "link": "product-a.html",
        "availability": "En stock",
        "published_date": "12/07/2026",
        "source_page": "https://example.com/catalogue.html",
    }
    item = normalize_item(raw)
    assert item is not None
    assert item.price == 19.90
    assert item.currency == "€"
    assert item.published_date.startswith("2026-07-12")


def test_deduplication_and_rejection():
    raw_items = [
        {
            "title": "Produit A",
            "price": "€ 19,90",
            "link": "product-a.html",
            "availability": "En stock",
            "published_date": "12/07/2026",
            "source_page": "https://example.com/catalogue.html",
        },
        {
            "title": "Produit A",
            "price": "€ 19,90",
            "link": "product-a.html",
            "availability": "En stock",
            "published_date": "12/07/2026",
            "source_page": "https://example.com/catalogue.html",
        },
        {
            "title": None,
            "price": "€ 19,90",
            "link": "product-b.html",
            "availability": "En stock",
            "published_date": "12/07/2026",
            "source_page": "https://example.com/catalogue.html",
        },
    ]

    normalized = normalize_items(raw_items)
    assert len(normalized) == 1
