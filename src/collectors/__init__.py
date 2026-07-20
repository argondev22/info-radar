"""コレクタのプラグイン登録・自動読み込み。

新しい取得方式（スクレイパー）を足すときは、**このディレクトリに1ファイル追加して
`@register("<kind>")` を付けるだけ**。既存ファイルは一切触らない（起動時に自動で読み込まれる）。

例（src/collectors/my_site.py）:
    from ..models import Item
    from ..sources import Source
    from . import register
    from .common import http_get

    @register("scrape_my_site")
    def collect_my_site(src: Source) -> list[Item]:
        ...
        return items

そして sources.yaml に `kind: scrape_my_site` のソースを足す。
"""
import importlib
import logging
import pkgutil
from typing import Callable

from ..models import Item
from ..sources import Source

log = logging.getLogger(__name__)

Collector = Callable[[Source], list[Item]]
_REGISTRY: dict[str, Collector] = {}
_loaded = False


def register(kind: str):
    """コレクタ関数を kind に紐付けて登録するデコレータ。"""
    def deco(fn: Collector) -> Collector:
        _REGISTRY[kind] = fn
        return fn
    return deco


def _ensure_loaded() -> None:
    global _loaded
    if _loaded:
        return
    for mod in pkgutil.iter_modules(__path__):
        if mod.name == "common":
            continue
        try:
            importlib.import_module(f"{__name__}.{mod.name}")
        except Exception as e:  # 壊れたプラグイン1つで全体を止めない
            log.warning("collector '%s' の読み込みに失敗: %s", mod.name, e)
    _loaded = True


def collect_source(src: Source) -> list[Item]:
    """kind に対応するコレクタで収集し、section を各記事へ引き継ぐ。"""
    _ensure_loaded()
    fn = _REGISTRY.get(src.kind)
    if fn is None:
        raise ValueError(f"unknown source kind: {src.kind}")
    items = fn(src)
    for it in items:
        it.section = src.section
    return items
