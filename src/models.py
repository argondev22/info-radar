"""収集した1記事を表す共通データ構造。"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Item:
    title: str
    url: str
    summary: str
    published: Optional[datetime]  # タイムゾーン付き。取れない場合は None
    category: str                  # "AWS" | "Claude" | "IT" …（= Notion の TAG）
    source_name: str               # ログ用（Notionには入れない）
    section: Optional[str] = None   # ページ内の並びグループ（任意。例: セキュリティ/AI/ツール）
