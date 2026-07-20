# CLAUDE.md — info-radar 運用ガイド（エージェント向け）

このリポジトリは AWS / Claude 等の最新情報を毎朝収集し、Notion に**カテゴリ別・日次ダイジェスト**を作る。
オペレーター（ユーザー）が「このソース追加して」「このカテゴリ追加して」等と言ったら、
下の**プレイブック**に従って**すぐ実行**すること。毎回ゼロから調べ直さない（必要な固定値は下に全部ある）。

## この基盤の要点

- パイプライン: 収集(RSS/スクレイプ) → 重複除去(`state/seen.json`) → Notion登録
- 出力: **新着があるカテゴリごとに1ページ/日**。タイトル=日付(JST)、TAG=カテゴリ、NOTE=ニュース、本文=記事のリンク箇条書き
- 登録先は**ユーザーの本番Notion**（`DB_APPLICATION_PAGES`）。他のDBには絶対に書き込まない。
- 実行: GitHub Actions 毎朝 06:00 JST（`.github/workflows/collect.yml`、cron `0 21 * * *` UTC）
- ローカル実行: `cd ~/Source/info-radar && source .venv/bin/activate && python -m src.main`
  （依存が無ければ `pip install -r requirements.txt`）

## ワークスペース固有の固定値（非秘密・調べ直し不要）

- 登録先 database_id: `24fd9401-0e58-806b-830f-eb48ba8f2997`（data_source: `24fd9401-0e58-802c-a221-000b1d032069`）
- NOTE「ニュース」ノート: `322d9401-0e58-80c9-b23e-c7153a5c9476`（= `config.NOTE_NEWS_ID`）
- タグDB（DB_APPLICATION_TAGS）の data_source: `6d33b54f-f36e-4eca-be7d-1aeeafdce04a`
- 既存タグ（**ニュース配下**）: AWS=`322d9401-0e58-8066-b57f-d326dc867242` / Claude=`3a2d9401-0e58-8057-9255-f920e10bd6eb`
  - ⚠ 同名タグが「Classmethod」ノート配下にも存在する。`NotionTarget.tag_id()` は
    「ニュース配下で名前一致」を自動選択するので、**タグIDは手で指定しない・ハードコードしない**。

## Notion 新API（データソース構造）の注意

- `pages.create` の parent は `{"type":"data_source_id","data_source_id":...}`（`database_id` 指定は使わない）
- `search` の `filter.value` は `"data_source"`（`"database"` は不可）
- データソースのスキーマ取得/クエリは `client.request(path="data_sources/{id}", ...)` / `.../{id}/query`

## プレイブック

### A. RSSソースを追加（最頻・数分）

1. `sources.yaml` に1エントリ追加（Python不要）：
   ```yaml
     - name: "<表示名>"
       category: "<カテゴリ>"
       kind: rss
       url: "<フィードURL>"
       section: "<任意: ページ内の並びグループ>"
   ```
2. 生存確認：`python -m src.main --dry-run` を実行し、そのソースの `collected N from ...` が出るか確認。
3. OKなら完了。必要なら CHANGELOG 追記＋リリース（→ E）。

### B. RSSが無いサイトを追加（スクレイプ）

1. `src/collectors/<name>.py` を**新規作成**（既存ファイルは触らない。`anthropic_news.py` が雛形）：
   ```python
   from bs4 import BeautifulSoup
   from ..models import Item
   from ..sources import Source
   from . import register
   from .common import http_get, clean_text, parse_date_text
   @register("scrape_<name>")
   def collect_<name>(src): ...  # Item のリストを返す
   ```
2. `sources.yaml` に `kind: scrape_<name>` でソース追加。
3. **必ず** `--dry-run` で件数と中身を確認（スクレイパーは壊れやすい。HTML構造は実物を見て書く）。

### C. カテゴリを追加（例：株式）

1. `sources.yaml` にそのカテゴリのソースを追加（`category: 株式`）。
   → コード（sources.py/config.py/main.py）は**触らない**（自動導出）。
2. 「ニュース」ノート配下に **`株式` タグ**を用意する。どちらか：
   - ユーザーに「Notionでニュース配下に株式タグ作って」と頼む、または
   - APIで作成（低リスク。不要なら archive で消せる）：
     ```python
     client.pages.create(
         parent={"type": "data_source_id", "data_source_id": "6d33b54f-f36e-4eca-be7d-1aeeafdce04a"},
         properties={
             "NAME": {"title": [{"text": {"content": "株式"}}]},
             "NOTE": {"relation": [{"id": "322d9401-0e58-80c9-b23e-c7153a5c9476"}]},
         },
     )
     ```
3. `--dry-run` で「株式」カテゴリが出るか確認。タグは実行時に名前で自動解決される。

### D. 変更を安全にテスト

- 収集だけ確認：`python -m src.main --dry-run`（書き込みなし）
- 実登録を試すなら、production 経路で数件だけ作り**必ず archive で消す**（`state/seen.json` は触らない）：
  `NotionTarget.create_category_digest(...)` → 検証 → `client.pages.update(page_id, archived=True)`
- 氾濫が怖い時は `--limit N` / 環境変数 `LOOKBACK_DAYS` / `MAX_PER_SOURCE` で調整。

### E. リリース

1. `CHANGELOG.md` の `[Unreleased]` に変更を記載（機能追加なら版セクションへ）
2. `git add -A && git commit -m "..." && git push`
3. 機能追加は MINOR を上げる：`git tag -a vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z`
   → `release.yml` が GitHub Release を自動作成。

## やってはいけない

- `.env` や `NOTION_TOKEN` をコミット/ログ出力しない（GitHub側は Secrets 登録済み）
- `DB_APPLICATION_PAGES` 以外のユーザーDBに書き込まない
- タグIDを手で指定/ハードコードしない（名前で自動解決される）
- 無確認で大量 backfill を本番投入しない（まず `--dry-run` / `--limit`）

## ファイル地図

```
sources.yaml       ★ソース定義（ここを編集: ソース/カテゴリ/並び順）
src/sources.py     sources.yaml のローダー（CATEGORY_ORDER/SECTION_ORDER導出）
src/collectors/    収集プラグイン（1 kind=1ファイル・@registerで自動登録）
  common.py        共通ヘルパー（http_get / clean_text / parse_date_text）
src/notion_sink.py Notion登録（NotionTarget: タグ自動解決・ページ組み立て）
src/main.py        ①収集 →②重複除去 →③登録
src/config.py      環境変数・NOTE_NEWS_ID
src/state.py       取り込み済みURL（seen.json）
.github/workflows/collect.yml  毎朝の定期実行
```
