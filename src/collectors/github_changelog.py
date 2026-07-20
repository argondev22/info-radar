"""GitHub 上の CHANGELOG.md 用コレクタ（kind: github_changelog）。最新1バージョンのみ。"""
import re

from .. import config
from ..models import Item
from ..sources import Source
from . import register
from .common import WS, http_get


@register("github_changelog")
def collect_github_changelog(src: Source) -> list[Item]:
    text = http_get(src.url).text
    items: list[Item] = []
    for block in re.split(r"^##\s+", text, flags=re.MULTILINE):
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        version = lines[0].strip()
        if not re.match(r"^v?\d+\.\d+", version):
            continue
        body = WS.sub(" ", " ".join(l.strip("-* ").strip() for l in lines[1:] if l.strip()))
        anchor = "v" + version.lstrip("v")
        url = f"https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md#{anchor}"
        items.append(
            Item(
                title=f"Claude Code {version}",
                url=url,
                summary=body[: config.NOTION_TEXT_LIMIT],
                published=None,
                category=src.category,
                source_name=src.name,
            )
        )
        break  # 最新の1バージョンのみ（パッチ版の氾濫を防ぐ）
    return items
