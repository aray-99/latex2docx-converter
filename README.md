# LaTeX to DOCX Converter

LaTeX 文書（特に日本語・jlreq・カスタムコマンド使用）を Microsoft Word（.docx）形式に変換するツール群です。

## 特徴

- ✨ **カスタムLaTeXコマンド対応** - physics2 の `\ab()` などのカスタムコマンドを自動変換
- 📊 **TikZ図の自動PNG変換** - TikZ 図を高解像度PNG画像に自動変換して docx に埋め込み
- 🇯🇵 **日本語文書対応** - jlreq クラス、LuaLaTeX に完全対応
- 🔄 **自動ラベル検出** - `\label{fig:...}` から TikZ ラベルを自動抽出
- 📁 **汎用性** - コマンドライン引数対応で任意のTeXファイルを処理可能

## インストール

### 必要な環境

- Python 3.7以上
- Bash (bash 4.0以上推奨)
- LaTeX (LuaLaTeX 推奨)
- Pandoc 2.0以上
- ImageMagick (PNG変換用)

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/latex2docx-converter.git
cd latex2docx-converter

# スクリプトに実行権限を付与
chmod +x src/*.sh
```

## 使用方法

### 基本的な使用例

```bash
# examples/basic ディレクトリで実行
cd examples/basic
../../src/convert_latex_to_docx.sh main.tex output.docx
```

### コマンドライン引数

```bash
# パターン1: 入力ファイルを指定
./src/convert_latex_to_docx.sh input.tex

# パターン2: 入力ファイルと出力ファイルを指定
./src/convert_latex_to_docx.sh input.tex output.docx

# パターン3: デフォルト（main.tex を読み込み、output_YYYYMMDD.docx を生成）
./src/convert_latex_to_docx.sh
```

### 生成ファイルのクリーンアップ

```bash
# 中間ファイルをすべて削除
./src/clean.sh
```

## ファイル構成

```
latex2docx-converter/
├── README.md                        # このファイル
├── LICENSE                          # MITライセンス
├── .gitignore                       # Git設定
├── src/
│   ├── convert_latex_to_docx.sh    # メイン変換スクリプト
│   ├── preprocess.py                # LaTeX前処理（カスタムコマンド変換）
│   ├── extract_tikz_improved.py     # TikZ図抽出（自動ラベル検出）
│   ├── compile_tikz_labeled.sh      # TikZ → PNG 変換
│   ├── replace_tikz_labeled.py      # TikZ → \includegraphics 置換
│   └── clean.sh                     # クリーンアップスクリプト
├── examples/
│   └── basic/                       # シンプルな使用例
│       ├── main.tex
│       ├── data/
│       │   └── sample.dat
│       └── figures/
└── docs/
    └── USAGE.md                     # 詳細な使用方法
```

## スクリプト説明

### 1. preprocess.py
LaTeX ファイルをpandoc変換用に前処理します。

**機能:**
- `\ab(...)` → `\left(...\right)` に変換（physics2対応）
- `\ab|...|` → `\left|...\right|` に変換
- `\ab{...}` → `\left{...\right}` に変換
- ネストされた括弧に対応

**使用例:**
```bash
python3 src/preprocess.py input.tex output_pandoc.tex
```

**コマンドライン引数:**
```
python3 preprocess.py [input_file] [output_file]
```

### 2. extract_tikz_improved.py
TikZ 図を抽出して standalone ファイルとして保存します。

**機能:**
- TeXファイルから TikZ 図を自動抽出
- `\label{fig:...}` から自動的にラベル検出
- データディレクトリ（data/）を自動コピー

**使用例:**
```bash
python3 src/extract_tikz_improved.py input.tex
```

**出力:**
- `tikz_extracted/` ディレクトリに standalone TeX ファイル
- `tikz_extracted/data/` に data ディレクトリのコピー

### 3. compile_tikz_labeled.sh
TikZ 図を PDF 経由で高解像度 PNG に変換します。

**機能:**
- 各 TikZ 図を個別にコンパイル（PDF化）
- PDF を 300dpi の PNG に変換
- pgfplots グラフも対応

**出力:**
- `tikz_png/` ディレクトリに PNG ファイル

### 4. replace_tikz_labeled.py
TikZ 環境を `\includegraphics` コマンドに置換します。

**機能:**
- 自動的にラベルを検出
- TikZ → `\includegraphics` に置換
- 画像の幅を自動調整

**使用例:**
```bash
python3 src/replace_tikz_labeled.py input_pandoc.tex output_with_images.tex
```

### 5. convert_latex_to_docx.sh
上記すべてを統合したメインスクリプトです。

**処理フロー:**
1. LaTeX前処理
2. TikZ図抽出
3. TikZ → PNG 変換
4. TikZ → 画像参照に置換
5. pandoc で docx に変換

## サンプル実行

```bash
# サンプルディレクトリに移動
cd examples/basic

# 実行（main.tex を output_YYYYMMDD.docx に変換）
../../src/convert_latex_to_docx.sh

# または、出力ファイル名を指定
../../src/convert_latex_to_docx.sh main.tex output.docx
```

### 出力ファイル

変換完了後、以下のファイルが生成されます：

```
examples/basic/
├── main_pandoc.tex                 # LaTeX前処理済みファイル
├── main_with_images.tex            # 画像参照置換済みファイル
├── output_YYYYMMDD.docx            # 最終出力ファイル（Word形式）
├── tikz_extracted/                 # 抽出されたTikZ figuresディレクトリ
│   ├── shapes.tex
│   ├── plot.tex
│   └── data/
├── tikz_png/                        # 生成されたPNG画像
│   ├── shapes.png
│   └── plot.png
├── compile.log                      # TikZコンパイルログ
└── pandoc_conversion.log            # pandocコンバージョンログ
```

## サポート対応

### サポートされるカスタムコマンド

- `physics2` パッケージの `\ab()`, `\ab||`, `\ab{}` など
- その他のカスタムコマンドは適宜追加可能

### サポートされる TikZ ライブラリ

- `tikz` 基本機能
- `pgfplots` （データプロット）
- `positioning`, `calc`, `patterns`, `arrows.meta`, `decorations.pathmorphing`
- `amsmath`, `amssymb`, `siunitx`

## トラブルシューティング

### TikZ コンパイル失敗

```bash
# ログを確認
cat compile.log
```

**よくある原因:**
- パッケージが未インストール → `tlmgr install` で追加
- 外部ファイル参照エラー → data/ ディレクトリが正しくコピーされているか確認

### pandoc 変換失敗

```bash
# ログを確認
cat pandoc_conversion.log
```

**よくある原因:**
- 画像ファイルパス不正 → pandoc のリソースパスを確認
- Unicode 文字化け → UTF-8 エンコーディングを確認

### LaTeX エラー

```bash
# 前処理ログを確認
python3 src/preprocess.py main.tex test.tex
```

## カスタマイズ

### カスタムコマンド追加

`src/preprocess.py` の `replace_ab_brackets()` 関数を拡張してください。

```python
# 例: \mycommand{...} をサポート
content = re.sub(r'\\mycommand\{(.+?)\}', r'\\textbf{\1}', content)
```

### TikZ 設定変更

`src/extract_tikz_improved.py` で standalone ファイルのプリアンブルをカスタマイズできます。

```python
standalone_content = f"""\\documentclass{{standalone}}
\\usepackage{{あなたのパッケージ}}
...
"""
```

## ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まず Issue を開いて変更内容を議論してください。

## 参考資料

- [Pandoc公式ドキュメント](https://pandoc.org/MANUAL.html)
- [TikZ & PGFPlots](https://tikz.dev/)
- [jlreq クラス](https://github.com/abenori/jlreq)
- [physics2 パッケージ](https://ctan.org/pkg/physics2)

## 既知の問題

- [ ] ネストした `\ab{...}` のエッジケースで失敗することがある
- [ ] 非常に大きな TikZ 図のコンパイルが遅い（>30秒）

## 更新履歴

### v0.1.0 (2026-01-15)

初版リリース

**機能:**
- コマンドライン引数対応
- 自動ラベル検出
- TikZ 自動 PNG 変換
- カスタムコマンド（physics2）対応
- 日本語文書完全対応

---

**質問や報告:** [Issues](https://github.com/yourusername/latex2docx-converter/issues) を開いてください
