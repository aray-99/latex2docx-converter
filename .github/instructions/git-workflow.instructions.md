---
applyTo: '**'
---

# Git Workflow Instructions

このファイルはGitHub Copilotおよび開発者向けの、汎用的なGit運用原則を定義します。

## 基本哲学

### 履歴の可読性 > コミット数の削減
- コミットは**意味のある単位**で分割する
- 後から見返したときに「なぜこの変更をしたか」が分かる履歴を維持
- 細かすぎる場合は`--squash`、意味のあるまとまりは`--no-ff`でマージ

### ブランチは作業の文脈を表現する
- ブランチ名から作業内容が推測できること
- 長期間残すブランチ（main/develop）と短期間のブランチを明確に区別
- 実験的な作業は`experiment/`プレフィックスを使用

---

## ブランチ戦略

### mainブランチ
- **目的**: 安定版の保管、リリース可能な状態を維持
- **保護**: 直接コミット禁止、必ずブランチ経由でマージ
- **履歴**: 重要な変更は`--no-ff`マージで分岐点を明示

### 作業ブランチの命名規則

| プレフィックス | 用途 | 例 | マージ方法 | 削除 |
|---------------|------|----|-----------|----|
| `feature/*` | 新機能開発 | `feature/argparse-support` | `--no-ff` | マージ後削除 |
| `experiment/*` | 実験的な試み | `experiment/new-algorithm` | `--no-ff` or `--squash` | マージ後削除 |
| `fix/*` | バグ修正 | `fix/escape-sequence` | `--no-ff` | マージ後削除 |
| `hotfix/*` | 緊急修正 | `hotfix/typo-in-readme` | `--ff-only` | マージ後削除 |
| `docs/*` | ドキュメント整備 | `docs/api-reference` | `--no-ff` | マージ後削除 |
| `refactor/*` | リファクタリング | `refactor/cleanup-scripts` | `--no-ff` | マージ後削除 |

### マージオプションの使い分け

#### `--no-ff` (No Fast-Forward)
```bash
git merge --no-ff feature/argparse-support
```

**用途**: 意味のある作業単位を履歴に残す
- 機能追加 (`feature/*`)
- 実験成功時 (`experiment/*`)
- 重要なバグ修正 (`fix/*`)
- ドキュメント整備 (`docs/*`)

**効果**: マージコミットが作成され、ブランチの存在が履歴に残る

#### `--squash`
```bash
git merge --squash experiment/trial-and-error
git commit -m "Add optimized algorithm after experimentation"
```

**用途**: 細かいコミットをまとめる
- 試行錯誤の繰り返し
- デバッグ・調整の履歴
- 複数の小さな変更

**効果**: 複数コミットが1つにまとめられ、履歴が簡潔に

#### `--ff-only` (Fast-Forward Only)
```bash
git merge --ff-only hotfix/typo
```

**用途**: 軽微な修正、履歴を汚さない
- タイポ修正
- コメント追加
- .gitignore 調整

**効果**: マージコミットが作成されず、直線的な履歴

---

## 試行錯誤時のGit活用

### 問題: ファイル名で試行版を管理
```bash
# ❌ 避けるべき
script.py
script_v2.py
script_final.py
script_FINAL.py
script_COMPLETE.py  # 混乱の元
```

### 解決策: Gitブランチで管理
```bash
# ✅ 推奨
git checkout -b experiment/approach-v1
# 試行錯誤
git add script.py
git commit -m "Try regex-based replacement"

git checkout -b experiment/approach-v2
# 別のアプローチ
git add script.py
git commit -m "Try pattern-based replacement"

# 成功したアプローチをmainにマージ
git checkout main
git merge --no-ff experiment/approach-v2
```

### タグで成功版を記録
```bash
git tag working-v1.0 -m "First working version"
# 後で参照可能
git checkout working-v1.0
```

---

## コミットメッセージ規約

### 基本フォーマット
```
<type>: <subject>

<body>

<footer>
```

### Type（日本語プロジェクトの場合）
| Type | 意味 | 例 |
|------|------|-----|
| `Add` | 新規追加 | `Add argument parsing support` |
| `Update` | 既存更新 | `Update README with usage examples` |
| `Fix` | バグ修正 | `Fix regex pattern for nested brackets` |
| `Refactor` | リファクタリング | `Refactor file I/O logic` |
| `Docs` | ドキュメント | `Docs: Add CONTRIBUTING.md` |
| `Remove` | 削除 | `Remove deprecated functions` |

### Subject（必須）
- 50文字以内
- 動詞で始める（Add, Update, Fix...）
- ピリオド不要
- 日本語・英語どちらでも可

### Body（任意）
- 72文字で改行
- **なぜこの変更が必要か**を記述
- **何を変更したか**は diff で分かるので省略可

### 例
```
Add command-line argument support

Hard-coded filenames made the script inflexible.
Users can now specify input/output files via arguments.

Closes #15
```

---

## 実践例：試行錯誤から成功まで

### 1. 実験ブランチで試行
```bash
git checkout -b experiment/auto-label-detection
# スクリプト修正・テスト
git commit -m "Try extracting labels from TeX file"
# 失敗
git commit -m "Fix regex pattern"
# まだ失敗
git commit -m "Use different approach with re.finditer"
# 成功！
```

### 2. 整理してmainにマージ
```bash
# オプション1: そのままマージ（履歴を保持）
git checkout main
git merge --no-ff experiment/auto-label-detection

# オプション2: squashしてまとめる
git checkout main
git merge --squash experiment/auto-label-detection
git commit -m "Add automatic TikZ label detection

Replace hard-coded label list with automatic extraction
from TeX file using regex pattern matching."
```

### 3. 実験ブランチを削除
```bash
git branch -d experiment/auto-label-detection
```

---

## ベストプラクティス

### DO（推奨）
- ✅ コミット前に `git diff` で変更内容を確認
- ✅ 意味のある単位でコミット（1機能 = 1コミット）
- ✅ プッシュ前に `git log --oneline --graph` で履歴確認
- ✅ ブランチ名に作業内容を含める
- ✅ 実験的な作業は `experiment/` ブランチで
- ✅ 成功した実験はタグを付ける

### DON'T（非推奨）
- ❌ mainブランチへの直接コミット
- ❌ "WIP", "fix", "update" だけのコミットメッセージ
- ❌ 1コミットに複数の機能追加
- ❌ ファイル名で版管理（script_v2.py, script_final.py等）
- ❌ force pushをmainブランチで使用
- ❌ マージ済みブランチを残したまま

### コミット前チェックリスト
```bash
# 1. 変更内容確認
git status
git diff

# 2. 不要なファイルが含まれていないか確認
git status | grep -E '\.(log|aux|pyc)$'
# → 何も表示されなければOK

# 3. ステージング
git add <files>

# 4. 再確認
git diff --staged

# 5. コミット
git commit -m "Type: Subject"

# 6. ログ確認
git log --oneline -3
```

---

## 緊急時の対応

### 間違ったブランチにコミット
```bash
# mainに直接コミットしてしまった
git reset --soft HEAD~1  # コミットを取り消し（変更は保持）
git switch -c feature/proper-branch
git commit -m "Proper commit message"
```

### コミットメッセージの修正
```bash
# 最新のコミットメッセージを修正
git commit --amend -m "Correct message"

# プッシュ済みの場合は避けるべき（どうしても必要なら）
git push --force-with-lease
```

### ブランチ削除ミス
```bash
# 誤ってブランチ削除
git reflog  # 削除前のコミットIDを探す
git switch -c feature/recovered <commit-id>
```

---

## まとめ

### 試行錯誤の黄金パターン
1. **実験開始**: `git checkout -b experiment/テーマ名`
2. **試行錯誤**: コミットを重ねる（失敗も含めて）
3. **成功確認**: 動作確認・テスト
4. **整理**: 必要に応じて`--squash`でまとめる
5. **マージ**: `git merge --no-ff experiment/テーマ名`
6. **後片付け**: `git branch -d experiment/テーマ名`

### 楽観的な命名を避ける
- ❌ `script_final.py`, `COMPLETE.sh`, `BEST_VERSION.py`
- ✅ `git tag v1.0-working`, `git tag experiment-success-20260115`

### ファイルではなくGitで版管理
- Gitブランチ・タグで履歴管理
- ファイル名はシンプルに保つ
- 試行錯誤はブランチで、成功版はタグで記録

---

**このファイルの役割**: GitHub Copilotがコード変更時に参照し、適切なGit操作を提案するための技術仕様書
