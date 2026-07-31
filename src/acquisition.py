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

    # 2. Page web distante via Playwright avec simulation utilisateur
    logging.info("Fetching %s via Playwright (Humain simulé)", source)

    with sync_playwright() as p:
        # Masque les indicateurs d'automatisation de Chrome
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )
        
        # Configuration complète du profil navigateur humain
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="fr-FR",
            timezone_id="Europe/Paris",
            permissions=["geolocation"],
        )
        
        page = context.new_page()

        # Supprime la propriété navigator.webdriver vue par les scripts anti-bot
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # Chargement de la page avec fallback réseau
        try:
            page.goto(source, wait_until="networkidle", timeout=15000)
        except Exception:
            page.goto(source, wait_until="domcontentloaded", timeout=15000)

        # Simulation des actions humaines
        page.mouse.move(200, 300)
        time.sleep(0.5)
        page.mouse.move(500, 400)
        
        # Scroll progressif pour déclencher le rendu dynamique du JS
        for _ in range(3):
            page.evaluate("window.scrollBy(0, 400)")
            time.sleep(0.5)

        time.sleep(delay_seconds)
        html_content = page.content()
        browser.close()

    return html_content