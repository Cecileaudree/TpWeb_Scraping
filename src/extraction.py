from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup


@dataclass
class RawItem:
    raw: Dict[str, Optional[str]]


def extract_next_page(html: str, page_url: str, next_page_selector: Optional[str]) -> Optional[str]:
    """Retourne l'URL absolue de la page suivante, ou None si absente/non configuree.

    Gere la pagination (module 02, chapitre 04) quand la cible expose un lien
    "suivant" (ex: ``a[rel='next']``). Retourne None sur la derniere page ou
    quand aucune pagination n'est configuree pour la cible.
    """
    if not next_page_selector:
        return None
    soup = BeautifulSoup(html, "html.parser")
    link = soup.select_one(next_page_selector)
    if link is None:
        return None
    href = link.get("href")
    if not href:
        return None
    return urljoin(page_url, href)


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
            # URL-like fields are extracted from href, other fields from visible text.
            if field_name in {"link", "url"} or field_name.endswith("_url"):
                raw[field_name] = selected.get("href")
            else:
                raw[field_name] = selected.get_text(strip=True)
        raw["source_page"] = start_page
        results.append(RawItem(raw=raw))
    return results
