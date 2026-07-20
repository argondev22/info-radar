"""Anthropic Newsroom スクレイパー（kind: scrape_anthropic_news）。"""
from bs4 import BeautifulSoup

from .. import config
from ..models import Item
from ..sources import Source
from . import register
from .common import WS, clean_text, http_get, parse_date_text


@register("scrape_anthropic_news")
def collect_anthropic_news(src: Source) -> list[Item]:
    soup = BeautifulSoup(http_get(src.url).text, "html.parser")
    items: list[Item] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].split("?")[0]
        if not href.startswith("/news/") or href == "/news/":
            continue
        url = "https://www.anthropic.com" + href
        if url in seen:
            continue
        # カードは2種類: featured=<h2/h4>にタイトル / grid=<span>にタイトル
        time_el = a.find("time")
        cat_span = time_el.parent.find("span") if (time_el and time_el.parent) else None
        heading = a.find(["h1", "h2", "h3", "h4", "h5"])
        if heading is not None:
            title = WS.sub(" ", heading.get_text(" ")).strip()
        else:
            title = ""
            for sp in a.find_all("span"):
                if sp is cat_span:  # カテゴリ(Product等)はスキップ
                    continue
                txt = WS.sub(" ", sp.get_text(" ")).strip()
                if len(txt) >= 4:
                    title = txt
                    break
        if len(title) < 4:
            continue
        seen.add(url)
        published = parse_date_text(time_el.get_text(" ")) if time_el else None
        p = a.find("p")
        summary = clean_text(p.get_text(" ")) if p else ""
        items.append(
            Item(
                title=title[: config.NOTION_TEXT_LIMIT],
                url=url,
                summary=summary,
                published=published,
                category=src.category,
                source_name=src.name,
            )
        )
        if len(items) >= config.MAX_PER_SOURCE:
            break
    return items
