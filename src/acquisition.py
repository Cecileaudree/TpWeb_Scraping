from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

import requests


def load_page(source: str, delay_seconds: float = 1.0) -> str:
    if source.startswith("file://"):
        content_path = Path(source[7:])
        return content_path.read_text(encoding="utf-8")

    local_path = Path(source)
    if local_path.exists():
        return local_path.read_text(encoding="utf-8")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; scraper/1.0; +https://example.com)"
    })
    logging.info("Fetching %s", source)
    response = session.get(source, timeout=20)
    response.raise_for_status()
    time.sleep(delay_seconds)
    return response.text
