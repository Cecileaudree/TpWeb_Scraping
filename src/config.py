from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urljoin


@dataclass
class TargetConfig:
    base_url: str
    start_page: str
    item_selector: str
    fields: Dict[str, str]
    # Selecteur CSS optionnel pointant vers le lien "page suivante" (pagination).
    # Laisse a None quand la cible tient sur une seule page (cas de l'echantillon S14).
    next_page_selector: Optional[str] = None


@dataclass
class ExportConfig:
    output_path: str
    format: str = "json"


@dataclass
class ScrapeConfig:
    delay_seconds: float = 1.0
    max_items: int = 0
    sample_mode: bool = False
    # Nombre maximal de pages a parcourir si une pagination est configuree.
    max_pages: int = 1


@dataclass
class Config:
    target: TargetConfig
    export: ExportConfig
    scrape: ScrapeConfig

    @classmethod
    def load(cls, path: str) -> "Config":
        config_path = Path(path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        target = TargetConfig(
            base_url=raw["target"].get("base_url", ""),
            start_page=raw["target"]["start_page"],
            item_selector=raw["target"]["item_selector"],
            fields=raw["target"]["fields"],
            next_page_selector=raw["target"].get("next_page_selector"),
        )
        export = ExportConfig(
            output_path=raw["export"]["output_path"],
            format=raw["export"].get("format", "json"),
        )
        scrape = ScrapeConfig(
            delay_seconds=float(raw["scrape"].get("delay_seconds", 1.0)),
            max_items=int(raw["scrape"].get("max_items", 0)),
            sample_mode=bool(raw["scrape"].get("sample_mode", False)),
            max_pages=int(raw["scrape"].get("max_pages", 1)),
        )
        return cls(target=target, export=export, scrape=scrape)

    def resolve_source(self) -> str:
        sample_page = Path("samples/sample_page.html")
        if self.scrape.sample_mode and sample_page.exists():
            return sample_page.as_posix()

        start_page = self.target.start_page

        if start_page.startswith(("http://", "https://", "file://")):
            return start_page

        if Path(start_page).exists():
            return start_page

        if self.scrape.sample_mode:
            return start_page

        if self.target.base_url:
            return urljoin(self.target.base_url.rstrip("/") + "/", start_page)

        return start_page
