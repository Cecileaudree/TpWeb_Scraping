from __future__ import annotations

import argparse
import logging
import time
from typing import List
from urllib.parse import urlparse

from .acquisition import load_page
from .config import Config
from .extraction import RawItem, extract_items, extract_next_page
from .exporter import export_items
from .normalization import normalize_items, NormalizedItem


def enforce_target_policies(source: str, delay_seconds: float) -> None:
    parsed = urlparse(source)
    hostname = (parsed.hostname or "").lower()
    if "aucklandmuseum.com" in hostname and delay_seconds < 30:
        raise ValueError(
            "La cible Auckland Museum impose un Crawl-delay de 30s: mettez scrape.delay_seconds >= 30"
        )


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run(config_path: str) -> int:
    started_at = time.perf_counter()
    config = Config.load(config_path)
    source = config.resolve_source()
    enforce_target_policies(source, config.scrape.delay_seconds)

    raw_dicts: List[dict] = []
    current_page = source
    pages_seen = 0
    max_pages = max(1, config.scrape.max_pages)

    for _ in range(max_pages):
        try:
            html = load_page(current_page, delay_seconds=config.scrape.delay_seconds)
        except Exception as exc:
            # Exemple d'erreur geree : une page inaccessible n'interrompt pas
            # le programme, elle est journalisee et le crawl s'arrete proprement.
            logging.error("Page inaccessible, arret du parcours: %s (%s)", current_page, exc)
            break

        pages_seen += 1
        raw_items: List[RawItem] = extract_items(
            html,
            current_page,
            config.target.item_selector,
            config.target.fields,
        )
        raw_dicts.extend(item.raw for item in raw_items)

        if config.scrape.max_items > 0 and len(raw_dicts) >= config.scrape.max_items:
            break

        next_page = extract_next_page(html, current_page, config.target.next_page_selector)
        if not next_page:
            break
        current_page = next_page

    normalized: List[NormalizedItem]
    normalized, stats = normalize_items(raw_dicts)
    if config.scrape.max_items > 0:
        normalized = normalized[: config.scrape.max_items]
    export_items(normalized, config.export.output_path, config.export.format)

    duration_ms = (time.perf_counter() - started_at) * 1000
    logging.info("Pages parcourues: %d", pages_seen)
    logging.info("Items vus: %d", stats.seen)
    logging.info("Items exportes: %d", len(normalized))
    logging.info("Items rejetes (champ obligatoire manquant): %d", stats.rejected)
    logging.info("Doublons ignores: %d", stats.duplicates)
    logging.info("Items avec champ optionnel manquant: %d", stats.missing_fields)
    logging.info("Duree totale de la collecte: %.1f ms", duration_ms)
    logging.info("Sortie ecrite: %s", config.export.output_path)

    if not normalized:
        logging.warning("Aucun item exporté. Vérifiez les sélecteurs et la page source.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Scraper explicable orienté S14")
    parser.add_argument("--config", default="config.example.json", help="Chemin vers le fichier de configuration JSON")
    args = parser.parse_args()
    configure_logging()
    try:
        return run(args.config)
    except Exception as exc:
        logging.error("Erreur lors de l'exécution: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
