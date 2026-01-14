#!/usr/bin/env python3
"""
Modern LaTeX to DOCX converter with integrated TikZ support.

A unified Python tool that converts LaTeX documents to Microsoft Word format
with automatic TikZ figure extraction and compilation.

Installation:
    pip install -e .

Usage:
    latex2docx main.tex                          # Convert main.tex → output_YYYYMMDD.docx
    latex2docx main.tex output.docx              # Specify output filename
    latex2docx main.tex output.docx --clean      # Clean intermediate files
    latex2docx --clean-only                      # Cleanup only
    latex2docx --help                            # Show help

Requirements:
    - pdflatex (from TeX Live or similar)
    - convert (from ImageMagick)
    - pandoc
"""

import sys
import logging
from pathlib import Path
from typing import Optional

from latex2docx.converter import TexConverter
from latex2docx.cli import main

if __name__ == '__main__':
    sys.exit(main())
