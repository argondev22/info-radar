"""コレクタ共通のヘルパー（HTTP取得・テキスト整形・日付パース）。"""
import re
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .. import config

WS = re.compile(r"\s+")

_MONTH_NAMES = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]
_MONTHS: dict[str, int] = {}
for _i, _m in enumerate(_MONTH_NAMES, start=1):
    _MONTHS[_m] = _i        # フルネーム: July
    _MONTHS[_m[:3]] = _i    # 3文字略記: Jul


def http_get(url: str) -> requests.Response:
    resp = requests.get(url, headers={"User-Agent": config.USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp


def clean_text(raw: str) -> str:
    if not raw:
        return ""
    text = BeautifulSoup(raw, "html.parser").get_text(" ")
    return WS.sub(" ", text).strip()[: config.NOTION_TEXT_LIMIT]


def struct_to_dt(st) -> Optional[datetime]:
    if not st:
        return None
    try:
        return datetime(*st[:6], tzinfo=timezone.utc)
    except Exception:
        return None


def parse_date_text(text: str) -> Optional[datetime]:
    """'July 15, 2026' / 'Jul 15, 2026' のような英語日付を拾う。"""
    m = re.search(r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", text)
    if not m:
        return None
    month = _MONTHS.get(m.group(1).lower())
    if not month:
        return None
    try:
        return datetime(int(m.group(3)), month, int(m.group(2)), tzinfo=timezone.utc)
    except Exception:
        return None
