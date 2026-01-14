---
applyTo: '**'
---

# TDD Instructions

このリポジトリは t-wada 風のTDD（Red → Green → Refactor）を採用します。

## 原則

- テストが仕様（最初にテストで期待値を固定）
- 失敗理由が分かる最小のテストを書く
- Greenの段階では「まず通す」、Refactorで設計を整える

## 実行

```bash
pytest -q
pytest -q tests/test_converter.py::TestBracketReplacement
```

## 変更時の指針

- 既存テストを壊したら、まず仕様のズレかバグかを切り分ける
- 外部依存（TeX/Pandoc/ImageMagick）に触れる処理は、ユニットテストではモック中心
- 変換パイプラインは「入力→出力」の観測点を増やし、原因特定しやすくする
