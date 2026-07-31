from __future__ import annotations

import logging
import time
from pathlib import Path
from playwright.sync_api import sync_playwright


def load_page(source: str, delay_seconds: float = 1.0) -> str:
    # 1. Gestion des fichiers locaux
    if source.startswith("file://"):
        content_path = Path(source[7:])
        return content_path.read_text(encoding="utf-8")

    local_path = Path(source)
    if local_path.exists():
        return local_path.read_text(encoding="utf-8")

    # 2. Page web distante via Playwright
    logging.info("Fetching %s via Playwright", source)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto(source, wait_until="domcontentloaded", timeout=30000)
        time.sleep(delay_seconds)
        html_content = page.content()
        browser.close()

    return html_content