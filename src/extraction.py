from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup


@dataclass
class RawItem:
    raw: Dict[str, Optional[str]]


def extract_next_page(html_or_data: Any, page_url: str, next_page_selector: Optional[str]) -> Optional[str]:
    if not next_page_selector or not isinstance(html_or_data, str):
        return None
    soup = BeautifulSoup(str(html_or_data), "html.parser")
    link = soup.select_one(next_page_selector)
    if link and link.get("href"):
        return urljoin(page_url, link.get("href"))
    return None


def extract_items(html_or_data: Any, start_page: str, item_selector: str, fields: Dict[str, str]) -> List[RawItem]:
    results: List[RawItem] = []

    # 1. Handle JSON Intercepted from Playwright
    data = html_or_data if isinstance(html_or_data, dict) else None
    if isinstance(html_or_data, str) and html_or_data.strip().startswith("{"):
        try:
            data = json.loads(html_or_data)
        except Exception:
            data = None

    if data:
        items_list = data.get("results", data.get("records", data.get("data", [])))
        if isinstance(items_list, dict):
            items_list = items_list.get("search", {}).get("results", [])

        for item in items_list:
            title = item.get("dc_title") or item.get("title") or "Collection Item"
            if isinstance(title, list) and title:
                title = title[0]

            item_id = item.get("id", "")
            url = f"https://www.aucklandmuseum.com/collections-research/collections/record/{item_id}" if item_id else start_page

            raw = {
                "title": str(title),
                "url": url,
                "category": str(item.get("department", ["Collection"])[0] if isinstance(item.get("department"), list) else "Collection"),
                "date_text": "N/A",
                "source_page": start_page
            }
            results.append(RawItem(raw=raw))

        if results:
            return results

    # 2. Fallback HTML Parser
    soup = BeautifulSoup(str(html_or_data), "html.parser")
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        text = link.get_text(strip=True)
        
        if len(text) > 3 and any(k in href for k in ["/collections/", "/record/", "/imagedata/"]):
            raw = {
                "title": text,
                "url": urljoin(start_page, href),
                "category": "Collection Item",
                "date_text": "N/A",
                "source_page": start_page
            }
            results.append(RawItem(raw=raw))

    return results