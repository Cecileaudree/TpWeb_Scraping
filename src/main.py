from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List

from .acquisition import load_page
from .config import Config
from .extraction import RawItem, extract_items
from .exporter import export_json
from .normalization import normalize_items, NormalizedItem


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run(config_path: str) -> int:
    config = Config.load(config_path)
    source = config.resolve_source()
    html = load_page(source, delay_seconds=config.scrape.delay_seconds)
    raw_items: List[RawItem] = extract_items(
        html,
        source,
        config.target.item_selector,
        config.target.fields,
    )
    raw_dicts = [item.raw for item in raw_items]
    normalized: List[NormalizedItem] = normalize_items(raw_dicts)
    export_json(normalized, config.export.output_path)

    logging.info("Items vus: %d", len(raw_items))
    logging.info("Items normalisés: %d", len(normalized))
    logging.info("Sortie écrite: %s", config.export.output_path)

    if not normalized:
        logging.warning("Aucun item exporté. Vérifiez les sélecteurs et la page source.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Scraper explicable de démonstration")
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
