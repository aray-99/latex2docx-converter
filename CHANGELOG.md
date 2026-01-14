# Changelog

このプロジェクトの変更履歴です。

形式は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) を参考にしつつ、厳密にはこだわりません。

## [Unreleased]

- TBD

## [v0.2.0] - 2026-01-15

### Added

- PythonパッケージとしてのCLI（`latex2docx`）
- TikZ抽出→PDF→PNG変換→`\includegraphics` 置換→pandoc変換の一括パイプライン
- GitHub Actions でのテスト実行（pytest）

### Changed

- README / docs を、初見ユーザーがコピペで使える形に整理
- 公開リポジトリとして不要・紛らわしいファイルの整理、履歴の見栄え改善

### Removed

- 内部向け引継ぎドキュメント等、公開に不要なもの

---

[v0.2.0]: https://github.com/aray-99/latex2docx-converter/releases/tag/v0.2.0

[Unreleased]: https://github.com/aray-99/latex2docx-converter/compare/v0.2.0...HEAD
