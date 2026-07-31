from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .normalization import NormalizedItem


def export_json(items: List[NormalizedItem], output_path: str) -> None:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump([item.to_dict() for item in items], handle, ensure_ascii=False, indent=2)


def export_jsonl(items: List[NormalizedItem], output_path: str) -> None:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item.to_dict(), ensure_ascii=False))
            handle.write("\n")


def export_items(items: List[NormalizedItem], output_path: str, format: str = "jsonl") -> None:
    if format == "json":
        export_json(items, output_path)
    elif format == "jsonl":
        export_jsonl(items, output_path)
    else:
        raise ValueError(f"Format d'export non supporte: {format}")
