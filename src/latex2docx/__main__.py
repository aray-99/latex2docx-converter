#!/usr/bin/env python3
"""
LaTeX to DOCX converter command-line entry point.
"""

import sys
from latex2docx.cli import main

if __name__ == '__main__':
    sys.exit(main())
