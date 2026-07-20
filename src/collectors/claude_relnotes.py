"""Claude Platform release notes スクレイパー（kind: scrape_claude_relnotes）。"""
from bs4 import BeautifulSoup

from .. import config
from ..models import Item
from ..sources import Source
from . import register
from .common import WS, http_get, parse_date_text


@register("scrape_claude_relnotes")
def collect_claude_relnotes(src: Source) -> list[Item]:
    soup = BeautifulSoup(http_get(src.url).text, "html.parser")
    items: list[Item] = []
    for h in soup.find_all(["h2", "h3"]):
        heading = WS.sub(" ", h.get_text(" ")).strip()
        dt = parse_date_text(heading)
        if dt is None:
            continue
        parts = []
        for sib in h.find_next_siblings():
            if getattr(sib, "name", None) in ("h1", "h2", "h3"):
                break
            parts.append(sib.get_text(" ") if hasattr(sib, "get_text") else str(sib))
        summary = WS.sub(" ", " ".join(parts)).strip()
        url = f"{src.url}#{dt.date().isoformat()}"
        items.append(
            Item(
                title=f"Claude Platform release notes ({dt.date().isoformat()})",
                url=url,
                summary=summary[: config.NOTION_TEXT_LIMIT],
                published=dt,
                category=src.category,
                source_name=src.name,
            )
        )
        if len(items) >= config.MAX_PER_SOURCE:
            break
    return items
