from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from dateutil.parser import parse as parse_date


@dataclass
class NormalizedItem:
    id: str
    source_url: str
    title: str
    price: float
    currency: str
    availability: str
    collected_at: str
    published_date: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_url": self.source_url,
            "title": self.title,
            "price": self.price,
            "currency": self.currency,
            "availability": self.availability,
            "collected_at": self.collected_at,
            "published_date": self.published_date,
        }


PRICE_RE = re.compile(r"(?P<currency>[€$£])?\s*(?P<amount>[0-9]+(?:[\.,][0-9]{1,2})?)")


def normalize_price(value: Optional[str]) -> Optional[Dict[str, Any]]:
    if not value:
        return None
    match = PRICE_RE.search(value)
    if not match:
        return None
    amount = match.group("amount").replace(",", ".")
    currency = match.group("currency") or "EUR"
    return {"price": float(amount), "currency": currency}


def normalize_date_string(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        parsed = parse_date(value, dayfirst=True)
        return parsed.isoformat()
    except Exception:
        logging.warning("Date normalization failed for %r", value)
        return None


def normalize_url(base_url: str, relative_url: Optional[str]) -> Optional[str]:
    if not relative_url:
        return None
    return urljoin(base_url, relative_url)


def normalize_item(raw: Dict[str, Optional[str]]) -> Optional[NormalizedItem]:
    title = raw.get("title")
    price_data = normalize_price(raw.get("price"))
    if not title or not price_data:
        return None

    raw_link = raw.get("link")
    source_url = normalize_url(raw.get("source_page", ""), raw_link) or raw.get("source_page", "")
    if not source_url:
        return None

    collected_at = datetime.now(timezone.utc).isoformat()
    published_date = normalize_date_string(raw.get("published_date"))
    availability = raw.get("availability") or "unknown"
    item_id = source_url
    return NormalizedItem(
        id=item_id,
        source_url=source_url,
        title=title,
        price=price_data["price"],
        currency=price_data["currency"],
        availability=availability,
        collected_at=collected_at,
        published_date=published_date,
    )


def normalize_items(raw_items: List[Dict[str, Optional[str]]]) -> List[NormalizedItem]:
    normalized: List[NormalizedItem] = []
    seen_ids: set[str] = set()
    for raw in raw_items:
        item = normalize_item(raw)
        if item is None:
            continue
        if item.id in seen_ids:
            continue
        seen_ids.add(item.id)
        normalized.append(item)
    return normalized
