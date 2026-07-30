from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from bs4 import BeautifulSoup


@dataclass
class RawItem:
    raw: Dict[str, Optional[str]]


def extract_items(html: str, start_page: str, item_selector: str, fields: Dict[str, str]) -> List[RawItem]:
    soup = BeautifulSoup(html, "html.parser")
    results: List[RawItem] = []
    for element in soup.select(item_selector):
        raw: Dict[str, Optional[str]] = {}
        for field_name, selector in fields.items():
            selected = element.select_one(selector)
            if selected is None:
                raw[field_name] = None
                continue
            if field_name == "link":
                raw[field_name] = selected.get("href")
            else:
                raw[field_name] = selected.get_text(strip=True)
        raw["source_page"] = start_page
        results.append(RawItem(raw=raw))
    return results
