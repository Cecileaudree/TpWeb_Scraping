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
