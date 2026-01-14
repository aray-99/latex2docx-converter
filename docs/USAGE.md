# Usage

このプロジェクトは、LaTeX文書（TikZ含む）を DOCX に変換するための Python CLI ツールです。

## クイックスタート

1) システム依存（LaTeX / ImageMagick / Pandoc）を入れる

- 詳細は .github/SYSTEM_REQUIREMENTS.md を参照

2) このツールをインストール

```bash
git clone https://github.com/aray-99/latex2docx-converter.git
cd latex2docx-converter
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

3) 変換を実行（main.tex と同じディレクトリで）

```bash
cd /path/to/your-latex-project
latex2docx main.tex
```

## 典型的なディレクトリ構成

`main.tex` と同じ階層で実行する前提です（相対パスの解決のため）。

```
your-project/
├── main.tex
├── data/        # TikZ/pgfplots が参照するデータ
├── figures/     # 画像など
└── sections/    # \input で分割している場合
```

## CLI オプション

```bash
latex2docx --help

latex2docx main.tex
latex2docx main.tex output.docx
latex2docx main.tex --clean
latex2docx --clean-only
latex2docx main.tex -v
```

## 生成物

```
your-project/
├── <stem>_pandoc.tex           # 前処理後TeX
├── <stem>_with_images.tex      # TikZ→\includegraphics 置換後TeX
├── output_YYYYMMDD.docx        # 生成DOCX
├── tikz_extracted/             # TikZ抽出（standalone化）
├── tikz_png/                   # PNG画像
├── compile.log                 # TikZコンパイルログ
└── pandoc_conversion.log       # pandocログ
```

`--clean` を付けると中間生成物は削除されます。

## トラブルシューティング

### TikZ のコンパイルが失敗する

- `pdflatex --version` が動くか確認
- `kpsewhich tikz.sty pgfplots.sty` でパッケージの有無を確認
- `compile.log` を確認

### DOCX 変換が失敗する

- `pandoc --version` を確認
- `pandoc_conversion.log` を確認

### ImageMagick の convert が動かない

- `convert --version` を確認
- Linux では policy.xml の制約で PDF を扱えない場合があります（ImageMagick の設定を確認してください）

## Customization

### Add Custom Commands

Edit `src/preprocess.py` to support additional commands:

```python
# Example: Support beamer's \alert{...}
def replace_custom_beamer(content):
    """Replace beamer commands"""
    content = re.sub(r'\\alert\{(.+?)\}', r'\\textcolor{red}{\1}', content)
    return content

# Add to process_tex_file()
content = replace_custom_beamer(content)
```

### Customize TikZ Preamble

Edit `src/extract_tikz_improved.py` to modify the TikZ preamble:

```python
standalone_content = f"""\\documentclass{{standalone}}
\\usepackage{{tikz}}
\\usepackage{{your-custom-package}}
...
"""
```

### Modify Pandoc Options

Edit `src/convert_latex_to_docx.sh` to change pandoc behavior:

```bash
# Current default
pandoc "$IMAGES_FILE" -o "${OUTPUT_FILE}" \
    --resource-path=.:tikz_png:data:figures \
    --number-sections \
    --toc \
    --standalone

# Example: Add bibliography and citation support
pandoc "$IMAGES_FILE" -o "${OUTPUT_FILE}" \
    --resource-path=.:tikz_png:data:figures \
    --toc \
    --standalone \
    --citeproc \
    --bibliography=refs.bib
```

## Configuration Files

### YAML Configuration (Planned Feature)

Future versions will support YAML configuration files:

```bash
# Planned usage (not yet implemented)
./src/convert_latex_to_docx.sh --config config.yaml
```

See `config.yaml.example` for the planned configuration format.

### Engine Selection (Planned Feature)

Future versions will support different LaTeX engines:

```bash
# Planned usage (not yet implemented)

# Use pdflatex (current default)
./src/convert_latex_to_docx.sh main.tex --engine pdflatex

# Use lualatex (future)
./src/convert_latex_to_docx.sh main.tex --engine lualatex

# Use xelatex (future)
./src/convert_latex_to_docx.sh main.tex --engine xelatex
```

## Tips and Tricks

### Handle Large TikZ Figures

For very large or complex TikZ figures:

```bash
# Option 1: Reduce PNG resolution
# Edit compile_tikz_labeled.sh and change 300 to 150 dpi

# Option 2: Break figure into multiple simpler figures
# Split one complex figure into several simpler ones

# Option 3: Use TikZ's external library
% In LaTeX preamble:
\tikzexternalize
```

### Batch Convert Multiple Documents

```bash
# Convert all TeX files in directory
for tex_file in *.tex; do
    ./src/convert_latex_to_docx.sh "$tex_file"
done
```

### Suppress PNG Embedding

If you don't want images embedded in docx:

```bash
# Skip step [4/5] and convert directly
./src/convert_latex_to_docx.sh main.tex  # Runs up to step [3/5]
# Manually run without image replacement
pandoc main_pandoc.tex -o output.docx \
    --number-sections --toc --standalone
```

## Q&A

**Q: Very large TikZ figure compiles slowly (>30 seconds)?**

A: Try these approaches:
1. Reduce PNG DPI (300→150)
2. Split complex figure into simpler ones
3. Use TikZ's `external` library for caching

**Q: Many warnings from Pandoc?**

A: Most warnings are related to Japanese text processing and can be ignored. The output is usually correct.

**Q: Can I use different LaTeX engines?**

A: Currently only pdflatex is supported. Future versions will support lualatex and xelatex. You can manually edit `compile_tikz_labeled.sh` to experiment.

**Q: How do I update just one figure?**

A: Manually edit the TikZ code in `tikz_extracted/` and re-run `./src/compile_tikz_labeled.sh`.

**Q: Which features are tested on?**

A: Currently tested on:
- Linux (Ubuntu 20.04+)
- macOS (11+)
- Bash 4.0+
- Python 3.7+
- TeX Live 2021+

---

For additional questions, please open an [Issue](https://github.com/yourusername/latex2docx-converter/issues).
