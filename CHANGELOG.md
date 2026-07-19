# Changelog

このプロジェクトの主な変更点を記録する。
書式は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/)、
版番号は [Semantic Versioning](https://semver.org/lang/ja/)（`MAJOR.MINOR.PATCH`）に従う。

- **MAJOR**: 互換性のない変更（例: Notionのスキーマ変更で既存DBが使えなくなる）
- **MINOR**: 後方互換のある機能追加（例: ソース追加、Claude要約の導入）
- **PATCH**: 後方互換のバグ修正・小改善

## [Unreleased]

## [0.1.0] - 2026-07-20
### Added
- AWS/Claude の5ソースからの情報収集
  - AWS What's New / AWS News Blog（RSS）
  - Claude Code CHANGELOG（GitHub raw・最新版のみ）
  - Anthropic Newsroom / Claude Platform release notes（スクレイプ）
- 収集結果を Notion に「1実行=1ダイジェストページ」として登録（AWS/Claudeセクション＋リンク箇条書き）
- `state/seen.json` による重複防止
- `LOOKBACK_DAYS` / `MAX_PER_SOURCE` による流入量の調整
- `--dry-run` / `--seed` の実行モード
- GitHub Actions による毎朝（07:00 JST）の定期実行

[Unreleased]: https://github.com/argondev22/info-radar/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/argondev22/info-radar/releases/tag/v0.1.0
