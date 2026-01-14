# Development Guide

このリポジトリは基本的に「一人開発」前提ですが、未来の自分（と、たまに現れる救世主）を助けるためのメモを残します。

## TL;DR

- ブランチを切る: `git switch -c fix/xxx` / `git switch -c feature/xxx`
- テストを回す: `pytest -q`
- リリースする: `gh release create vX.Y.Z --generate-notes`

## Git（推奨フロー）

### `checkout`より`switch`/`restore`

- ブランチ切り替え/作成: `git switch`
- ステージングの取り消し/ファイル復元: `git restore`

例:

```bash
# ブランチ作成
git switch -c feature/something

# 変更を一部だけステージ
git add -p

# ステージング取り消し
git restore --staged path/to/file

# ファイルを元に戻す
git restore path/to/file
```

### ブランチ運用

- 直接`main`にコミットしない（小さくてもブランチ経由）
- マージ後に作業ブランチは削除（ローカルは `git branch -d ...`）

### コミットメッセージ

- 先頭にTypeを付ける（例: `Add:` `Fix:` `Docs:` `Refactor:` `Remove:`）
- 「何を」より「なぜ」をBodyに書く（必要なときだけ）

## gh CLI（GitHub操作）

### リポジトリ作成

```bash
gh repo create aray-99/latex2docx-converter --public --source=. --remote=origin --push
```

### Release作成（タグも同時に作る）

```bash
gh release create v0.2.1 --target main --title "v0.2.1" --generate-notes
```

### よく使う確認

```bash
gh repo view --web

gh release list

gh workflow list

gh run list
```

## TDD（テスト駆動）

このプロジェクトは t-wada 流の「Red → Green → Refactor」を意識しています。

- Red: 期待する振る舞いをテストで固定
- Green: とにかく通す（キレイさは後回し）
- Refactor: 読みやすく、壊れにくく

### テスト実行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

pip install -r requirements-dev.txt
pytest -q
```

### 書き方の目安

- まずは小さく1ケース
- 追加ケースは失敗の理由が分かる粒度で
- 仕様の言語化（テスト名/テストのArrange部分）は丁寧に

## 参考

- Git運用の詳細: `.github/instructions/git-workflow.instructions.md`
- TikZの設計原則: `.github/instructions/tikz.instructions.md`
