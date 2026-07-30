from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.extraction import extract_items, extract_next_page
from src.normalization import normalize_item, normalize_items


def load_sample_html() -> str:
    path = Path(__file__).resolve().parent.parent / "samples" / "sample_page.html"
    return path.read_text(encoding="utf-8")


def test_extract_items_count():
    html = load_sample_html()
    items = extract_items(
        html,
        "samples/sample_page.html",
        ".collection-item",
        {
            "title": ".item-title",
            "url": ".item-link",
            "category": ".item-category",
            "date_text": ".item-date",
        },
    )
    assert len(items) == 3


def test_normalize_item_s14_shape():
    raw = {
        "title": "Tiki carved pendant",
        "url": "/discover/collections/item-a",
        "category": "Ethnology",
        "date_text": "circa 1880",
        "source_page": "https://example.com/catalogue.html",
    }
    fixed_now = datetime(2026, 7, 30, 10, 0, 0, tzinfo=timezone.utc)
    item, missing = normalize_item(raw, collected_at=fixed_now)
    assert item is not None
    assert missing is False
    assert item.title == "Tiki carved pendant"
    assert item.category == "Ethnology"
    assert item.date_text == "circa 1880"
    assert item.url == "https://example.com/discover/collections/item-a"
    # Normalisation "date et heure de collecte, avec le fuseau" (exigence du TP).
    assert item.collected_at == "2026-07-30T10:00:00+00:00"


def test_normalize_item_missing_optional_field_is_marked():
    # category est absente du dictionnaire brut (cle non fournie) : elle doit
    # etre distinguee d'un champ present mais vide, via la sentinelle "inconnu".
    raw = {
        "title": "Objet sans categorie",
        "url": "/discover/collections/item-z",
        "date_text": "",
        "source_page": "https://example.com",
    }
    item, missing = normalize_item(raw)
    assert item is not None
    assert missing is True
    assert item.category == "inconnu"
    # date_text est presente mais vide : elle reste une chaine vide, pas "inconnu".
    assert item.date_text == ""


def test_deduplication_and_rejection():
    raw_items = [
        {
            "title": "Tiki carved pendant",
            "url": "/discover/collections/item-a",
            "category": "Ethnology",
            "date_text": "circa 1880",
            "source_page": "https://example.com/catalogue.html",
        },
        {
            "title": "Tiki carved pendant",
            "url": "/discover/collections/item-a",
            "category": "Ethnology",
            "date_text": "circa 1880",
            "source_page": "https://example.com/catalogue.html",
        },
        {
            "title": None,
            "url": "/discover/collections/item-b",
            "category": "Archaeology",
            "date_text": "1901",
            "source_page": "https://example.com/catalogue.html",
        },
    ]

    normalized, stats = normalize_items(raw_items)
    assert len(normalized) == 1
    assert stats.seen == 3
    assert stats.accepted == 1
    assert stats.rejected == 1
    assert stats.duplicates == 1


def test_max_items_slice_behavior():
    raw_items = [
        {
            "title": "Item A",
            "url": "/a",
            "category": "C1",
            "date_text": "1900",
            "source_page": "https://example.com",
        },
        {
            "title": "Item B",
            "url": "/b",
            "category": "C2",
            "date_text": "1901",
            "source_page": "https://example.com",
        },
        {
            "title": "Item C",
            "url": "/c",
            "category": "C3",
            "date_text": "1902",
            "source_page": "https://example.com",
        },
    ]
    normalized, _stats = normalize_items(raw_items)
    assert len(normalized[:2]) == 2


def test_extract_next_page_absent_without_selector():
    html = load_sample_html()
    assert extract_next_page(html, "samples/sample_page.html", None) is None

