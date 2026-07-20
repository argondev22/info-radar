"""RSS / Atom フィード用コレクタ（kind: rss）。"""
import feedparser

from .. import config
from ..models import Item
from ..sources import Source
from . import register
from .common import clean_text, http_get, struct_to_dt


@register("rss")
def collect_rss(src: Source) -> list[Item]:
    feed = feedparser.parse(http_get(src.url).content)
    items: list[Item] = []
    for e in feed.entries[: config.MAX_PER_SOURCE]:
        link = e.get("link")
        title = e.get("title")
        if not link or not title:
            continue
        summary = clean_text(e.get("summary", "") or e.get("description", ""))
        published = struct_to_dt(e.get("published_parsed") or e.get("updated_parsed"))
        items.append(
            Item(
                title=title.strip(),
                url=link,
                summary=summary,
                published=published,
                category=src.category,
                source_name=src.name,
            )
        )
    return items
