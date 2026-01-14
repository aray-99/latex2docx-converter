"""
Test configuration and fixtures for latex2docx.
"""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def sample_tex_file(temp_dir):
    """Create a minimal LaTeX file for testing."""
    tex_content = r"""\documentclass{article}
\usepackage{tikz}

\begin{document}
\section{Test Section}

This is a test with $\ab(x+y)$ bracket notation.

\begin{figure}
\begin{tikzpicture}
\draw (0,0) -- (1,1);
\end{tikzpicture}
\caption{Test Figure}
\label{fig:test}
\end{figure}

\end{document}
"""
    tex_file = temp_dir / "test.tex"
    tex_file.write_text(tex_content, encoding='utf-8')
    return tex_file


@pytest.fixture
def sample_tikz_tex(temp_dir):
    """Create a LaTeX file with TikZ figures."""
    tex_content = r"""\documentclass{article}
\usepackage{tikz}
\usepackage{pgfplots}

\begin{document}

\begin{figure}
\begin{tikzpicture}
\draw (0,0) circle (1cm);
\end{tikzpicture}
\caption{Circle}
\label{fig:circle}
\end{figure}

\begin{figure}
\begin{tikzpicture}
\draw (0,0) rectangle (2,1);
\end{tikzpicture}
\caption{Rectangle}
\label{fig:rectangle}
\end{figure}

\end{document}
"""
    tex_file = temp_dir / "tikz_test.tex"
    tex_file.write_text(tex_content, encoding='utf-8')
    return tex_file
