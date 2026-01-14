# System Requirements

This project requires the following system-level software to be installed.

## Required System Dependencies

### 1. LaTeX Distribution

**Purpose**: Compile TikZ figures to PDF

**Required packages**:
- `pdflatex` - LaTeX compiler
- `tikz` - Graphics package
- `pgfplots` - Plot package
- Standard LaTeX packages (`amsmath`, `amssymb`, `siunitx`, etc.)

**Installation**:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended

# macOS (Homebrew)
brew install --cask mactex

# Arch Linux
sudo pacman -S texlive-core texlive-latexextra
```

### 2. ImageMagick

**Purpose**: Convert PDF to PNG images (300 DPI)

**Installation**:

```bash
# Ubuntu/Debian
sudo apt-get install imagemagick

# macOS (Homebrew)
brew install imagemagick

# Arch Linux
sudo pacman -S imagemagick
```

### 3. Pandoc

**Purpose**: Convert LaTeX to DOCX format

**Installation**:

```bash
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS (Homebrew)
brew install pandoc

# Arch Linux
sudo pacman -S pandoc
```

## Python Requirements

**Python Version**: 3.8 or higher

**Python Packages**: None (uses only standard library)

The converter script uses only Python standard library modules:
- `re`, `os`, `sys`, `pathlib`
- `subprocess`, `shutil`
- `argparse`, `datetime`

## Verification

To verify all dependencies are installed correctly:

```bash
# Check LaTeX
pdflatex --version

# Check ImageMagick
convert --version

# Check Pandoc
pandoc --version

# Check Python
python3 --version
```

## Optional Dependencies

For development and testing:

```bash
pip install -r requirements-dev.txt
```

See [`requirements-dev.txt`](../requirements-dev.txt) for details.
