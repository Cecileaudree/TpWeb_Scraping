from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import Config, ExportConfig, ScrapeConfig, TargetConfig
from src.exporter import export_jsonl
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
    assert item.collected_at == "2026-07-30T10:00:00+00:00"


def test_normalize_item_missing_optional_field_is_marked():
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


def test_export_jsonl_writes_one_object_per_line(tmp_path):
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
    ]
    normalized, _stats = normalize_items(raw_items)
    output_path = tmp_path / "output.jsonl"
    export_jsonl(normalized, str(output_path))

    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    for line in lines:
        obj = json.loads(line)
        assert "id" in obj and "title" in obj


def test_resolve_source_uses_base_url_for_relative_remote_paths():
    config = Config(
        target=TargetConfig(
            base_url="https://www.aucklandmuseum.com",
            start_page="/collections-research/collections",
            item_selector=".collection-item",
            fields={"title": ".item-title"},
        ),
        export=ExportConfig(output_path="samples/output.jsonl", format="jsonl"),
        scrape=ScrapeConfig(sample_mode=False),
    )

    assert config.resolve_source() == "https://www.aucklandmuseum.com/collections-research/collections"


def test_resolve_source_prefers_sample_page_in_sample_mode():
    config = Config(
        target=TargetConfig(
            base_url="https://www.aucklandmuseum.com",
            start_page="https://www.aucklandmuseum.com/discover/collections/search?k=brooch",
            item_selector="article a[href^='/discover/collections/record/']",
            fields={"title": "h2.search-results--heading"},
        ),
        export=ExportConfig(output_path="samples/output.jsonl", format="jsonl"),
        scrape=ScrapeConfig(sample_mode=True),
    )

    assert config.resolve_source() == "samples/sample_page.html"


def test_extract_items_supports_self_selector():
    html = """
    <article>
      <a href="/discover/collections/record/71156?k=brooch">
        <h2 class="search-results--heading">brooch</h2>
        <div class="search-results--info">
          <p class="search-results--info-details">
            <span><strong>Collection: </strong> HUMAN HISTORY</span>
            <span><strong>Accession Number: </strong> 1973.162</span>
            <span><strong>Accession Date: </strong> 28 Aug 1973</span>
          </p>
        </div>
      </a>
    </article>
    """

    items = extract_items(
        html,
        "https://www.aucklandmuseum.com/discover/collections/search?k=brooch",
        "article a[href^='/discover/collections/record/']",
        {
            "title": "h2.search-results--heading",
            "url": "self",
            "category": "p.search-results--info-details span:nth-of-type(1)",
            "date_text": "p.search-results--info-details span:nth-of-type(3)",
        },
    )

    assert len(items) == 1
    assert items[0].raw["title"] == "brooch"
    assert items[0].raw["url"] == "/discover/collections/record/71156?k=brooch"
    assert "HUMAN HISTORY" in (items[0].raw["category"] or "")
    assert "28 Aug 1973" in (items[0].raw["date_text"] or "")
