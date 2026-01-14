# LaTeX to DOCX Converter 詳細な使用方法

このドキュメントでは、LaTeX to DOCX Converter の詳細な使用方法とカスタマイズについて説明します。

## 目次

1. [基本的な使用方法](#基本的な使用方法)
2. [スクリプト別の詳細](#スクリプト別の詳細)
3. [トラブルシューティング](#トラブルシューティング)
4. [カスタマイズ](#カスタマイズ)
5. [設定ファイル](#設定ファイル)

## 基本的な使用方法

### クイックスタート

```bash
# 例1: デフォルト設定で変換（main.tex → output_YYYYMMDD.docx）
cd your-project-dir
/path/to/latex2docx-converter/src/convert_latex_to_docx.sh

# 例2: 入力ファイルを指定
/path/to/latex2docx-converter/src/convert_latex_to_docx.sh mydoc.tex

# 例3: 入力・出力ファイルを指定
/path/to/latex2docx-converter/src/convert_latex_to_docx.sh input.tex output.docx
```

### ディレクトリ構造の推奨レイアウト

```
your-project/
├── main.tex                 # メインのTeXファイル
├── data/                    # 外部データファイル（CSV等）
│   └── sample.dat
├── figures/                 # 図のソース（EPS等）
│   └── sample.eps
└── sections/                # サブセクション（\input で参照）
    ├── 01-intro.tex
    ├── 02-methods.tex
    └── 03-results.tex
```

**重要:** 変換スクリプトは main.tex と同じディレクトリから実行してください。外部ファイル参照が正しく解決されます。

## スクリプト別の詳細

### 1. convert_latex_to_docx.sh（メインスクリプト）

全プロセスを一括実行します。

#### 使用方法

```bash
./src/convert_latex_to_docx.sh [input_file] [output_file]
```

#### パラメータ

| 引数 | 説明 | デフォルト |
|------|------|----------|
| input_file | 入力TeXファイル | main.tex |
| output_file | 出力docxファイル | output_YYYYMMDD.docx |

#### 出力

```
your-project/
├── main_pandoc.tex              # 前処理済みTeXファイル
├── main_with_images.tex         # 画像置換済みTeXファイル
├── output_20260115.docx         # 最終出力（Word形式）
├── tikz_extracted/              # 抽出されたTikZ figuresディレクトリ
│   ├── shapes.tex
│   ├── plot.tex
│   └── data/                    # dataディレクトリのコピー
├── tikz_png/                    # 生成されたPNG画像
│   ├── shapes.png
│   └── plot.png
├── compile.log                  # TikZコンパイルログ
└── pandoc_conversion.log        # Pandocコンバージョンログ
```

### 2. preprocess.py

LaTeXカスタムコマンドを標準コマンドに変換します。

#### 使用方法

```bash
python3 src/preprocess.py [input_file] [output_file]
```

#### サポートされる変換

| 入力 | 出力 | 対応パッケージ |
|------|------|--------------|
| `\ab(x)` | `\left(x\right)` | physics2 |
| `\ab\|x\|` | `\left\|x\right\|` | physics2 |
| `\ab{x}` | `\left\{x\right\}` | physics2 |

#### ネストされた括弧の対応

```latex
% 入力
\ab(\ab(a) + b)

% 出力
\left(\left(a\right) + b\right)
```

最大50回の反復処理でネストに対応しています。

### 3. extract_tikz_improved.py

TeXファイルからTikZ図を抽出します。

#### 使用方法

```bash
python3 src/extract_tikz_improved.py [input_file]
```

#### 自動ラベル検出

TeXファイル内の `\label{fig:...}` コマンドから自動的にラベルを検出します。

```latex
\begin{figure}
\begin{tikzpicture}
  % TikZ code
\end{tikzpicture}
\caption{Sample figure}
\label{fig:sample-diagram}
\end{figure}
```

上記の場合、抽出ファイルは `tikz_extracted/sample-diagram.tex` となります。

#### データディレクトリの自動コピー

`data/` ディレクトリが存在する場合、自動的に `tikz_extracted/data/` にコピーされます。TikZ 内で `table {data/sample.dat}` と参照している場合、正常にコンパイルされます。

### 4. compile_tikz_labeled.sh

TikZ図をコンパイルしてPNGに変換します。

#### 使用方法

```bash
./src/compile_tikz_labeled.sh
```

#### 処理内容

1. `tikz_extracted/` 内の各 `.tex` ファイルを pdflatex でコンパイル
2. 生成された PDF を ImageMagick で PNG に変換（300dpi）

#### トラブルシューティング

**コンパイル失敗時:**

```bash
# コンパイルログを確認
cat compile.log
```

**よくある原因と対策:**

| 問題 | 原因 | 対策 |
|------|------|------|
| `! Package pgfplots Error` | pgfplotsパッケージが未インストール | `tlmgr install pgfplots` |
| `! Undefined control sequence` | カスタムパッケージが未対応 | [カスタマイズ](#カスタマイズ)参照 |
| PNG生成失敗 | ImageMagick がインストールされていない | `sudo apt install imagemagick` |

### 5. replace_tikz_labeled.py

TikZ 環境を `\includegraphics` コマンドに置換します。

#### 使用方法

```bash
python3 src/replace_tikz_labeled.py [input_file] [output_file]
```

#### 処理例

```latex
% 入力（main_pandoc.tex）
\begin{tikzpicture}
  \draw (0,0) rectangle (2,1);
\end{tikzpicture}

% 出力（main_with_images.tex）
\begin{center}
\includegraphics[width=0.8\textwidth]{tikz_png/sample-diagram.png}
\end{center}
```

### 6. clean.sh

生成されたすべての一時ファイルを削除します。

#### 使用方法

```bash
./src/clean.sh
```

#### 削除対象

- `tikz_extracted/` ディレクトリ
- `tikz_png/` ディレクトリ
- `*_pandoc.tex`, `*_with_images.tex`
- `*.docx` ファイル
- ログファイル (`compile.log`, `pandoc_conversion.log`)

## トラブルシューティング

### よくある問題と解決方法

#### 1. TikZ コンパイルエラー

**症状:** `[3/5]` のステップで失敗

```bash
# ステップ
echo "エラー: TikZ図のコンパイルに失敗しました"
```

**原因と対策:**

```bash
# 1. ログを確認
cat compile.log | tail -20

# 2. 必要なパッケージをインストール
tlmgr install pgfplots amsmath amssymb

# 3. 再度実行
./src/compile_tikz_labeled.sh
```

#### 2. Pandoc 変換エラー

**症状:** `[5/5]` のステップで失敗

```bash
# ステップ
echo "エラー: pandoc変換に失敗しました"
```

**原因と対策:**

```bash
# 1. ログを確認
cat pandoc_conversion.log

# 2. Pandoc をアップグレード
pandoc --version  # バージョン確認
# Version 2.10以上が必要です

# 3. リソースパスを確認
ls -la tikz_png/
ls -la data/

# 4. 再度実行
./src/convert_latex_to_docx.sh
```

#### 3. 文字化け

**症状:** docx ファイルで日本語が文字化けしている

**原因:**
- TeX ファイルが UTF-8 でエンコードされていない
- Pandoc の文字エンコーディング設定不正

**対策:**

```bash
# 1. TeXファイルのエンコーディングを確認
file main.tex
# 出力例: main.tex: UTF-8 Unicode text

# 2. UTF-8 に変換する場合
iconv -f SJIS -t UTF-8 main.tex > main_utf8.tex
mv main_utf8.tex main.tex
```

#### 4. 画像が表示されない

**症状:** docx ファイルに画像が埋め込まれていない

**原因:**
- TikZ コンパイル失敗（PNG 生成失敗）
- パスが相対パスになっていない

**対策:**

```bash
# 1. PNG ファイルが生成されているか確認
ls -la tikz_png/

# 2. ファイルが空でないか確認
file tikz_png/*.png

# 3. 生のLaTeXで確認
pdflatex main_with_images.tex
```

## カスタマイズ

### カスタムコマンドの追加

physics2 以外のパッケージのコマンドを対応させたい場合、`preprocess.py` を編集します。

#### 例：beamer の `\alert{...}` に対応

```python
# preprocess.py の replace_ab_brackets() 関数の後に追加

def replace_custom_beamer(content):
    """beamerコマンドを置換"""
    # \alert{...} を \textcolor{red}{...} に置換
    content = re.sub(r'\\alert\{(.+?)\}', r'\\textcolor{red}{\1}', content)
    return content

# process_tex_file() 内で呼び出し
content, iterations = replace_ab_brackets(content)
content = replace_custom_beamer(content)  # 追加
```

### TikZ プリアンブルのカスタマイズ

TikZ 図の抽出時に使用するプリアンブルを変更したい場合、`extract_tikz_improved.py` を編集します。

```python
# extract_tikz_improved.py の standalone_content 定義部分

standalone_content = f"""\\documentclass{{standalone}}
\\usepackage{{tikz}}
\\usetikzlibrary{{パッケージ1,パッケージ2}}
\\usepackage{{あなたのカスタムパッケージ}}

\\begin{{document}}
{tikz_code}
\\end{{document}}
"""
```

### Pandoc オプションの変更

`convert_latex_to_docx.sh` の pandoc コマンドを編集します。

```bash
# 現在
pandoc "$IMAGES_FILE" -o "${OUTPUT_FILE}" \
    --resource-path=.:tikz_png:data:figures \
    --number-sections \
    --toc \
    --standalone

# カスタマイズ例：セクション番号なし、参考文献機能追加
pandoc "$IMAGES_FILE" -o "${OUTPUT_FILE}" \
    --resource-path=.:tikz_png:data:figures \
    --toc \
    --standalone \
    --citeproc \
    --bibliography=refs.bib
```

## 設定ファイル

### YAML 設定ファイルのサポート（将来実装予定）

将来的には YAML 設定ファイルでカスタマイズできるようにする予定です。

```bash
# 使用方法（未実装）
./src/convert_latex_to_docx.sh --config config.yaml
```

設定ファイルの例は `config.yaml.example` を参照してください。

### エンジン選択（将来実装予定）

LaTeX エンジンを切り替える機能を実装予定です。

```bash
# pdflatex を使用（現在はこれのみ）
./src/convert_latex_to_docx.sh main.tex --engine pdflatex

# lualatex を使用（将来）
./src/convert_latex_to_docx.sh main.tex --engine lualatex

# xelatex を使用（将来）
./src/convert_latex_to_docx.sh main.tex --engine xelatex
```

---

## Q&A

**Q: 非常に大きなTikZ図でコンパイルが遅い場合は？**

A: 以下を試してください：
1. TikZ の `external` ライブラリを使用
2. `tikz_png` のDPI を下げる（300→150 など）
3. 複雑な図を複数の簡単な図に分割

**Q: Pandoc で多くの警告が出る場合は？**

A: ほとんどの場合、日本語処理に関する警告です。通常は無視して大丈夫です。

**Q: どうしても PNG 埋め込みしたくない場合は？**

A: `convert_latex_to_docx.sh` の `[4/5]` ステップをスキップして、直接 `main_pandoc.tex` を pandoc で変換してください（ただしTikZ図は表示されません）。

**Q: 複数のTeXファイルを一括変換したい場合は？**

A: bash ループで対応できます：
```bash
for tex_file in *.tex; do
    ./src/convert_latex_to_docx.sh "$tex_file"
done
```

---

最後に、バグ報告や機能リクエストは [GitHub Issues](https://github.com/yourusername/latex2docx-converter/issues) をお使いください。
