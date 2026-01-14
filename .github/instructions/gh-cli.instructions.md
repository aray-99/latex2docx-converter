---
applyTo: '**'
---

# gh CLI Instructions

このリポジトリでGitHub操作をするときの、`gh`（GitHub CLI）用メモ。

## 目的

- ブラウザに行かずに、リポジトリ操作・リリース・Actions確認を完結させる
- 手順をコマンドで残し、再現性を高める

## よく使うコマンド

### 状態確認

```bash
gh auth status
gh repo view --web
gh release list
gh workflow list
gh run list
```

### リリース

```bash
# タグ作成 + Release作成（自動ノート）
gh release create vX.Y.Z --target main --title "vX.Y.Z" --generate-notes

# 既存Releaseの編集
gh release edit vX.Y.Z --title "..." --notes "..."
```

### リポジトリ設定（About/Topics）

```bash
gh repo edit <OWNER>/<REPO> --description "..." --homepage "..." --add-topic latex --add-topic pandoc
```
