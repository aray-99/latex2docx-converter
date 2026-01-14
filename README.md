# LaTeX to DOCX Converter

Convert LaTeX documents (especially with Japanese text, jlreq class, and custom commands) to Microsoft Word (.docx) format.

## Features

- ✨ **Custom LaTeX Commands Support** - Automatically converts custom commands like physics2's `\ab()` notation
- 📊 **Automatic TikZ-to-PNG Conversion** - High-resolution PNG conversion of TikZ figures embedded in docx
- 🇯🇵 **Japanese Document Support** - Full support for jlreq class, LuaLaTeX, and Unicode text
- 🔄 **Automatic Label Detection** - Automatically extracts TikZ labels from `\label{fig:...}` commands
- 📁 **Generalized Design** - Command-line arguments support for processing any LaTeX file

## Installation

### Requirements

- Python 3.7+
- Bash (4.0+ recommended)
- LaTeX (LuaLaTeX recommended)
- Pandoc 2.0+
- ImageMagick (for PNG conversion)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/latex2docx-converter.git
cd latex2docx-converter

# Make scripts executable
chmod +x src/*.sh
```

## Quick Start

### Basic Usage

```bash
# Navigate to your LaTeX project directory
cd your-project-dir

# Convert main.tex to output.docx
/path/to/converter/src/convert_latex_to_docx.sh main.tex output.docx
```

### Command-line Arguments

```bash
# Pattern 1: Specify input file only
./src/convert_latex_to_docx.sh input.tex

# Pattern 2: Specify both input and output files
./src/convert_latex_to_docx.sh input.tex output.docx

# Pattern 3: Use defaults (main.tex → output_YYYYMMDD.docx)
./src/convert_latex_to_docx.sh
```

### Cleanup Generated Files

```bash
# Remove all intermediate files
./src/clean.sh
```

## Project Structure

```
latex2docx-converter/
├── README.md                        # This file
├── LICENSE                          # MIT License
├── .gitignore                       # Git settings
├── src/
│   ├── convert_latex_to_docx.sh    # Main conversion script
│   ├── preprocess.py                # LaTeX preprocessing (custom commands)
│   ├── extract_tikz_improved.py     # TikZ figure extraction
│   ├── compile_tikz_labeled.sh      # TikZ → PNG conversion
│   ├── replace_tikz_labeled.py      # TikZ → \includegraphics replacement
│   └── clean.sh                     # Cleanup script
├── examples/
│   ├── basic/                       # Japanese example
│   │   ├── main.tex
│   │   ├── data/
│   │   │   └── sample.dat
│   │   └── figures/
│   └── english/                     # English example
│       ├── main.tex
│       ├── data/
│       │   └── sample.dat
│       └── figures/
├── docs/
│   └── USAGE.md                     # Detailed usage guide
└── config.yaml.example              # Configuration template
```

## Script Overview

### 1. preprocess.py

Preprocesses LaTeX files for pandoc conversion.

**Features:**
- Converts `\ab(...)` → `\left(...\right)` (physics2 support)
- Converts `\ab|...|` → `\left|...\right|`
- Converts `\ab{...}` → `\left{...\right}`
- Handles nested brackets

**Usage:**
```bash
python3 src/preprocess.py input.tex output.tex
```

### 2. extract_tikz_improved.py

Extracts TikZ figures from LaTeX files.

**Features:**
- Automatic TikZ figure extraction
- Automatic label detection from `\label{fig:...}`
- Auto-copies data directory for pgfplots support

**Usage:**
```bash
python3 src/extract_tikz_improved.py input.tex
```

**Output:**
- `tikz_extracted/` directory with standalone TeX files
- `tikz_extracted/data/` with copy of data directory

### 3. compile_tikz_labeled.sh

Converts TikZ figures to high-resolution PNG images.

**Features:**
- Compiles each TikZ figure to PDF
- Converts PDF to PNG at 300 dpi
- Supports pgfplots graphs

**Output:**
- `tikz_png/` directory with PNG files

### 4. replace_tikz_labeled.py

Replaces TikZ environments with `\includegraphics` commands.

**Usage:**
```bash
python3 src/replace_tikz_labeled.py input.tex output.tex
```

**Example:**
```latex
% Input
\begin{tikzpicture}
  \draw (0,0) rectangle (2,1);
\end{tikzpicture}

% Output
\begin{center}
\includegraphics[width=0.8\textwidth]{tikz_png/diagram.png}
\end{center}
```

### 5. convert_latex_to_docx.sh

Main conversion script that orchestrates the entire process.

**Processing Steps:**
1. Preprocess LaTeX file
2. Extract TikZ figures
3. Convert TikZ to PNG
4. Replace TikZ with image references
5. Convert to docx with pandoc

## Example Output

After running the converter:

```
your-project/
├── main_pandoc.tex                 # Preprocessed file
├── main_with_images.tex            # Image-replaced file
├── output.docx                     # Final output (Word format)
├── tikz_extracted/                 # Extracted TikZ figures
│   ├── shapes.tex
│   ├── plot.tex
│   └── data/
├── tikz_png/                       # Generated PNG images
│   ├── shapes.png
│   └── plot.png
├── compile.log                     # TikZ compilation log
└── pandoc_conversion.log           # Pandoc conversion log
```

## Supported Custom Commands

The converter supports custom LaTeX commands from various packages:

| Package | Command | Conversion |
|---------|---------|-----------|
| physics2 | `\ab(x)` | `\left(x\right)` |
| physics2 | `\ab\|x\|` | `\left\|x\right\|` |
| physics2 | `\ab{x}` | `\left\{x\right\}` |

Additional commands can be added by extending `preprocess.py`.

## Supported TikZ Libraries

- Core tikz package
- pgfplots (data visualization)
- positioning, calc, patterns
- arrows.meta, decorations.pathmorphing
- amsmath, amssymb, siunitx

## Troubleshooting

### TikZ Compilation Fails

```bash
# Check the log
cat compile.log

# Common causes:
# - Missing LaTeX packages: tlmgr install <package>
# - External file reference errors: check data/ directory
```

### Pandoc Conversion Fails

```bash
# Check the log
cat pandoc_conversion.log

# Common causes:
# - Image path issues: verify tikz_png/ directory exists
# - Encoding issues: ensure UTF-8 encoding
```

### Images Not Displaying in DOCX

```bash
# Verify PNG files were generated
ls -la tikz_png/

# Check file integrity
file tikz_png/*.png
```

## Customization

### Add Custom Commands

Edit `src/preprocess.py` to add new command conversions:

```python
def replace_custom_beamer(content):
    """Replace beamer commands"""
    content = re.sub(r'\\alert\{(.+?)\}', r'\\textcolor{red}{\1}', content)
    return content

# Call in process_tex_file()
content = replace_custom_beamer(content)
```

### Customize TikZ Preamble

Edit `src/extract_tikz_improved.py` to change the standalone document preamble:

```python
standalone_content = f"""\\documentclass{{standalone}}
\\usepackage{{your-custom-package}}
...
"""
```

### Modify Pandoc Options

Edit `src/convert_latex_to_docx.sh` to change pandoc options:

```bash
pandoc "$IMAGES_FILE" -o "${OUTPUT_FILE}" \
    --resource-path=.:tikz_png:data:figures \
    --number-sections \
    --toc \
    --standalone \
    --citeproc \
    --bibliography=refs.bib
```

## Examples

This repository includes two examples:

- **examples/basic/** - Japanese LaTeX document demonstrating Unicode support
- **examples/english/** - English LaTeX document

Run either example:

```bash
cd examples/basic
../../src/convert_latex_to_docx.sh main.tex output.docx

cd ../english
../../src/convert_latex_to_docx.sh main.tex output.docx
```

## Future Enhancements

Planned features (see `config.yaml.example`):

- YAML configuration file support
- Configurable LaTeX engine (pdflatex, lualatex, xelatex)
- Batch conversion mode
- Custom stylesheet support for docx output

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## References

- [Pandoc Documentation](https://pandoc.org/MANUAL.html)
- [TikZ & PGFPlots](https://tikz.dev/)
- [jlreq Class](https://github.com/abenori/jlreq)
- [physics2 Package](https://ctan.org/pkg/physics2)

## Support

For bug reports, feature requests, and questions, please open an [Issue](https://github.com/yourusername/latex2docx-converter/issues).

---

**Latest Version:** v0.1.0  
**Last Updated:** 2026-01-15
