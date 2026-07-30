from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

# Sentinelle utilisee pour distinguer un champ absent (cle manquante dans le
# dictionnaire brut) d'un champ present mais vide ou nul. Un champ absent est
# remplace par "inconnu" et compte dans les statistiques de champs manquants ;
# un champ present mais vide reste une chaine vide "".
MISSING_FIELD_VALUE = "inconnu"

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(value: Optional[str]) -> str:
    """Normalisation texte : compresse les espaces multiples et coupe les bords."""
    if not value:
        return ""
    return _WHITESPACE_RE.sub(" ", value).strip()


def normalize_url(base_url: str, relative_url: Optional[str]) -> Optional[str]:
    """Normalisation URL : resout une URL relative contre l'URL source."""
    if not relative_url:
        return None
    return urljoin(base_url, relative_url)


@dataclass
class NormalizedItem:
    id: str
    title: str
    category: str
    date_text: str
    url: str
    collected_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "date_text": self.date_text,
            "url": self.url,
            "collected_at": self.collected_at,
        }


@dataclass
class NormalizationStats:
    seen: int = 0
    accepted: int = 0
    rejected: int = 0
    duplicates: int = 0
    missing_fields: int = 0


def _read_optional_field(raw: Dict[str, Optional[str]], name: str) -> Tuple[str, bool]:
    """Lit un champ optionnel en distinguant absence et valeur vide.

    - Cle absente du dictionnaire brut -> champ considere comme manquant,
      remplace par MISSING_FIELD_VALUE ("inconnu") et signale (is_missing=True).
    - Cle presente mais valeur None/"" -> champ present mais vide, conserve
      tel quel sous forme de chaine vide (is_missing=False).
    """
    if name not in raw:
        return MISSING_FIELD_VALUE, True
    value = raw.get(name)
    text = normalize_text(value)
    return text, False


def normalize_item(
    raw: Dict[str, Optional[str]],
    collected_at: Optional[datetime] = None,
) -> Tuple[Optional["NormalizedItem"], bool]:
    """Normalise un objet brut. Retourne (item ou None, champ_manquant_detecte)."""
    title = normalize_text(raw.get("title"))
    if not title:
        return None, False

    raw_url = raw.get("url") or raw.get("link")
    normalized_url = normalize_url(raw.get("source_page", ""), raw_url)
    if not normalized_url:
        return None, False

    category, category_missing = _read_optional_field(raw, "category")
    date_text, date_missing = _read_optional_field(raw, "date_text")

    timestamp = (collected_at or datetime.now(timezone.utc)).isoformat()

    item = NormalizedItem(
        id=normalized_url,
        title=title,
        category=category,
        date_text=date_text,
        url=normalized_url,
        collected_at=timestamp,
    )
    return item, (category_missing or date_missing)


def normalize_items(
    raw_items: List[Dict[str, Optional[str]]],
    collected_at: Optional[datetime] = None,
) -> Tuple[List[NormalizedItem], NormalizationStats]:
    stats = NormalizationStats(seen=len(raw_items))
    normalized: List[NormalizedItem] = []
    seen_ids: set[str] = set()
    now = collected_at or datetime.now(timezone.utc)
    for raw in raw_items:
        item, missing = normalize_item(raw, collected_at=now)
        if item is None:
            stats.rejected += 1
            continue
        if item.id in seen_ids:
            stats.duplicates += 1
            continue
        seen_ids.add(item.id)
        if missing:
            stats.missing_fields += 1
        normalized.append(item)
    stats.accepted = len(normalized)
    return normalized, stats
