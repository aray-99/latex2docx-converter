# LaTeX to DOCX Converter

A modern Python tool that converts LaTeX documents to Microsoft Word (.docx) format with integrated TikZ support.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-26%20passing-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- ✨ **Modern Python Package** - Clean, maintainable codebase with type hints and pathlib
- 🧪 **TDD Test Suite** - 26 unit tests following t-wada methodology (100% passing)
- 📊 **TikZ Integration** - Automatic extraction, compilation, and PNG conversion
- 🔄 **Auto Label Detection** - Extracts figure labels from `\label{fig:...}` automatically
- 🇯🇵 **Japanese Support** - Full support for jlreq, LuaLaTeX, and Unicode text
- 🛠️ **Custom Commands** - Automatically converts physics2 `\ab()` notation and custom macros
- 🎯 **Single Entry Point** - One command for the entire conversion pipeline

## Installation

### System Requirements

- **Python**: 3.10 or higher
- **LaTeX**: TeX Live or similar (provides `pdflatex`)
- **ImageMagick**: For PDF to PNG conversion
- **Pandoc**: For LaTeX to DOCX conversion

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install texlive-latex-base texlive-latex-extra imagemagick pandoc python3
```

#### macOS (Homebrew)

```bash
brew install --cask mactex
brew install imagemagick pandoc python
```

### Package Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/latex2docx-converter.git
cd latex2docx-converter

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

## Quick Start

### Basic Usage

```bash
# Add src to PYTHONPATH and run
cd /path/to/your-latex-project
PYTHONPATH=/path/to/latex2docx-converter/src python3 -m latex2docx main.tex

```

### Command-Line Options

```bash
# Show help
PYTHONPATH=src python3 -m latex2docx --help

# Convert with automatic cleanup
PYTHONPATH=src python3 -m latex2docx main.tex output.docx --clean

# Cleanup only (remove intermediate files)
PYTHONPATH=src python3 -m latex2docx --clean-only

# Verbose output
PYTHONPATH=src python3 -m latex2docx main.tex -v
```

## Project Structure

```
latex2docx-converter/
├── README.md                        # This file
├── LICENSE                          # MIT License
├── setup.py                         # Package setup
├── requirements.txt                 # System dependencies documentation
├── requirements-dev.txt             # Development dependencies
├── pytest.ini                       # Test configuration
├── .gitignore                       # Git settings
├── src/
│   └── latex2docx/                  # Main Python package
│       ├── __init__.py              # Package entry point
│       ├── __main__.py              # python -m support
│       ├── cli.py                   # Command-line interface
│       └── converter.py             # Core conversion logic
├── tests/                           # TDD test suite
│   ├── conftest.py                  # Test fixtures
│   ├── test_cli.py                  # CLI tests (6 tests)
│   └── test_converter.py            # Converter tests (20 tests)
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
└── .github/
    ├── instructions/                # Development guidelines
    │   ├── git-workflow.instructions.md
    │   └── tikz.instructions.md
    └── SYSTEM_REQUIREMENTS.md      # Detailed system dependencies
```

## How It Works

### Conversion Pipeline

```
1. Preprocessing          → Convert custom commands (\ab notation)
2. TikZ Extraction        → Extract TikZ figures as standalone files
3. TikZ Compilation       → Compile to PDF, convert to PNG (300 DPI)
4. TikZ Replacement       → Replace \begin{tikzpicture} with \includegraphics
5. Pandoc Conversion      → Convert LaTeX to DOCX
6. Cleanup (optional)     → Remove intermediate files
```

### Module Overview

#### `converter.py` - Core Logic

The `TexConverter` class handles the entire conversion pipeline:

```python
from latex2docx.converter import TexConverter

converter = TexConverter('main.tex', 'output.docx')
converter.preprocess_tex()      # Step 1
converter.extract_tikz()         # Step 2
converter.compile_tikz()         # Step 3
converter.replace_tikz()         # Step 4
converter.convert_to_docx()      # Step 5
converter.cleanup()              # Step 6 (optional)
```

**Key Features:**
- Uses `pathlib.Path` for cross-platform compatibility
- Type hints for better code clarity
- Logging module for proper output
- Handles nested bracket replacement (physics2 `\ab` notation)
- Automatic label detection from `\label{fig:...}`

#### `cli.py` - Command-Line Interface

Provides user-friendly CLI with argparse:

```bash
latex2docx input.tex [output.docx] [--clean] [--verbose]
latex2docx --clean-only  # Cleanup mode
```

## Development

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
PYTHONPATH=src pytest tests/ -v

# Run specific test class
PYTHONPATH=src pytest tests/test_converter.py::TestBracketReplacement -v

# Run with coverage (requires pytest-cov)
PYTHONPATH=src pytest tests/ --cov=latex2docx --cov-report=html
```

### Test-Driven Development

This project follows t-wada TDD methodology:

1. **Red**: Write tests first
2. **Green**: Make tests pass
3. **Refactor**: Clean up code

**Current Test Coverage:**
- ✅ 26 unit tests (100% passing)
- ✅ Bracket replacement tests
- ✅ Label extraction tests  
- ✅ TikZ extraction tests
- ✅ CLI interface tests
- ✅ Cleanup functionality tests

## Example Workflow

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
├── compile.log                     # TikZ compilation log (if not cleaned)
└── pandoc_conversion.log           # Pandoc log (if not cleaned)
```

With `--clean` option, intermediate files are automatically removed after conversion.

## Examples

This repository includes two example projects:

### Basic Example (Japanese)

```bash
cd examples/basic
PYTHONPATH=../../src python3 -m latex2docx main.tex output.docx --clean
```

### English Example

```bash
cd examples/english  
PYTHONPATH=../../src python3 -m latex2docx main.tex output.docx --clean
```

Both examples demonstrate:
- TikZ figure handling
- pgfplots integration
- Data directory auto-copying
- Custom command conversion

## Troubleshooting

### TikZ Compilation Fails

```bash
# Check if pdflatex is installed
pdflatex --version

# Verify TikZ packages
kpsewhich tikz.sty pgfplots.sty

# Inspect compilation log (if --clean not used)
cat compile.log
```

### Pandoc Conversion Fails

```bash
# Verify pandoc installation
pandoc --version

# Check conversion log
cat pandoc_conversion.log

# Test pandoc manually
pandoc test.tex -o test.docx
```

### Images Not in DOCX

- Verify PNG files exist: `ls -la tikz_png/`
- Check image paths in `*_with_images.tex`
- Ensure ImageMagick is installed: `convert --version`

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8, use type hints (Python 3.10+)
- **Testing**: Write tests first (TDD methodology)
- **Commits**: Follow [Git Workflow Instructions](.github/instructions/git-workflow.instructions.md)
- **TikZ**: Follow [TikZ Design Principles](.github/instructions/tikz.instructions.md)

### Running Tests

```bash
# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install pytest

# Run all tests
PYTHONPATH=src pytest tests/ -v

# Run specific test file
PYTHONPATH=src pytest tests/test_converter.py -v

# Run with coverage
pip install pytest-cov
PYTHONPATH=src pytest tests/ --cov=latex2docx --cov-report=term-missing
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/new-feature`
2. Write tests first (TDD Red phase)
3. Implement feature (TDD Green phase)
4. Refactor code (TDD Refactor phase)
5. Merge with `--no-ff`: `git merge --no-ff feature/new-feature`

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a Pull Request

## References

- [Pandoc User's Guide](https://pandoc.org/MANUAL.html)
- [TikZ & PGF Manual](https://tikz.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

**Developed with ❤️ using TDD methodology**

**Latest Version:** v0.1.0  
**Last Updated:** 2026-01-15
