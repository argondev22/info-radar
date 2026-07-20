"""ソース定義の読み込み。`sources.yaml`（リポジトリ直下）から Source 一覧を構築する。

ソース/カテゴリ/並び順の追加・変更は **sources.yaml を編集するだけ**でよい。このファイルは触らない。
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

SOURCES_YAML = Path(__file__).resolve().parent.parent / "sources.yaml"


@dataclass
class Source:
    name: str
    category: str
    kind: str
    url: str
    section: Optional[str] = None  # ページ内の並びグループ（任意）
    key: str = ""


def _load_sources() -> list[Source]:
    data = yaml.safe_load(SOURCES_YAML.read_text(encoding="utf-8")) or {}
    out: list[Source] = []
    for i, row in enumerate(data.get("sources", [])):
        out.append(
            Source(
                name=row["name"],
                category=row["category"],
                kind=row["kind"],
                url=row["url"],
                section=row.get("section"),
                key=row.get("key", f"src{i}"),
            )
        )
    return out


SOURCES = _load_sources()

# カテゴリの表示順（sources.yaml の登場順）
CATEGORY_ORDER = list(dict.fromkeys(s.category for s in SOURCES))

# ページ内の section 並び順（sources.yaml の登場順）
SECTION_ORDER = list(dict.fromkeys(s.section for s in SOURCES if s.section))


def section_rank(section: Optional[str]) -> int:
    """ページ内の並び順。section 無し(None)は先頭、以降は sources.yaml の登場順。"""
    if section is None:
        return -1
    return SECTION_ORDER.index(section) if section in SECTION_ORDER else len(SECTION_ORDER)
