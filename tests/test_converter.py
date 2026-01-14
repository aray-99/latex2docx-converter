"""
Unit tests for TexConverter class.

Following TDD principles:
1. Write tests first (Red)
2. Make tests pass (Green)
3. Refactor
"""

import pytest
from pathlib import Path
from latex2docx.converter import TexConverter


class TestTexConverterInit:
    """Test TexConverter initialization."""
    
    def test_init_with_existing_file(self, sample_tex_file):
        """Test initialization with an existing file."""
        converter = TexConverter(sample_tex_file)
        assert converter.input_path == sample_tex_file
        assert converter.input_path.exists()
    
    def test_init_with_nonexistent_file(self, temp_dir):
        """Test initialization fails with non-existent file."""
        nonexistent = temp_dir / "nonexistent.tex"
        with pytest.raises(FileNotFoundError):
            TexConverter(nonexistent)
    
    def test_init_generates_output_filename(self, sample_tex_file):
        """Test that output filename is auto-generated."""
        converter = TexConverter(sample_tex_file)
        assert converter.output_path.name.startswith('output_')
        assert converter.output_path.suffix == '.docx'
    
    def test_init_with_custom_output(self, sample_tex_file):
        """Test initialization with custom output filename."""
        output_file = "custom_output.docx"
        converter = TexConverter(sample_tex_file, output_file)
        assert converter.output_path.name == output_file


class TestBracketReplacement:
    """Test \\ab(...) bracket replacement."""
    
    def test_simple_bracket_replacement(self):
        """Test simple \\ab(x) replacement."""
        content = r"Test $\ab(x+y)$ here"
        result, iterations = TexConverter._replace_ab_brackets(content)
        assert r"\left(x+y\right)" in result
        assert r"\ab(" not in result
    
    def test_nested_bracket_replacement(self):
        """Test nested bracket replacement."""
        content = r"$\ab(x + \ab(y+z))$"
        result, iterations = TexConverter._replace_ab_brackets(content)
        assert r"\left(x + \left(y+z\right)\right)" in result
    
    def test_pipe_bracket_replacement(self):
        """Test \\ab|x| replacement."""
        content = r"$\ab|x|$"
        result, iterations = TexConverter._replace_ab_brackets(content)
        assert r"\left|x\right|" in result
    
    def test_brace_replacement(self):
        """Test \\ab\\{x\\} replacement."""
        content = r"$\ab\{x\}$"
        result, iterations = TexConverter._replace_ab_brackets(content)
        assert r"\left\{x\right\}" in result


class TestLabelExtraction:
    """Test label extraction from LaTeX."""
    
    def test_extract_single_label(self):
        """Test extracting a single figure label."""
        content = r"\label{fig:test}"
        labels = TexConverter._extract_labels(content)
        assert 'test' in labels
    
    def test_extract_multiple_labels(self):
        """Test extracting multiple labels."""
        content = r"""
        \label{fig:first}
        \label{fig:second}
        \label{fig:third}
        """
        labels = TexConverter._extract_labels(content)
        assert len(labels) == 3
        assert 'first' in labels
        assert 'second' in labels
        assert 'third' in labels
    
    def test_extract_no_labels(self):
        """Test with content that has no labels."""
        content = "No labels here"
        labels = TexConverter._extract_labels(content)
        assert len(labels) == 0


class TestStandaloneTex:
    """Test standalone TeX generation."""
    
    def test_standalone_tex_contains_tikz(self):
        """Test that standalone TeX wraps TikZ code properly."""
        tikz_code = r"\draw (0,0) -- (1,1);"
        result = TexConverter._make_standalone_tex(tikz_code)
        
        assert r"\documentclass{standalone}" in result
        assert r"\usepackage{tikz}" in result
        assert r"\begin{document}" in result
        assert tikz_code in result
        assert r"\end{document}" in result
    
    def test_standalone_tex_has_required_packages(self):
        """Test that standalone includes necessary packages."""
        tikz_code = r"\draw (0,0) circle (1);"
        result = TexConverter._make_standalone_tex(tikz_code)
        
        assert r"\usepackage{pgfplots}" in result
        assert r"\usepackage{amsmath,amssymb,bm,siunitx}" in result
        assert r"\usetikzlibrary" in result


class TestPreprocessing:
    """Test TeX preprocessing."""
    
    def test_preprocess_creates_pandoc_file(self, sample_tex_file, temp_dir):
        """Test that preprocessing creates output file."""
        converter = TexConverter(sample_tex_file)
        converter.preprocess_tex()
        
        assert converter.pandoc_path.exists()
        content = converter.pandoc_path.read_text()
        assert len(content) > 0
    
    def test_preprocess_replaces_brackets(self, sample_tex_file):
        """Test that preprocessing replaces \\ab brackets."""
        converter = TexConverter(sample_tex_file)
        converter.preprocess_tex()
        
        content = converter.pandoc_path.read_text()
        assert r"\ab(" not in content
        assert r"\left(" in content or r"$" not in content


class TestTikzExtraction:
    """Test TikZ figure extraction."""
    
    def test_extract_creates_directory(self, sample_tikz_tex):
        """Test that extraction creates tikz_extracted directory."""
        converter = TexConverter(sample_tikz_tex)
        count = converter.extract_tikz()
        
        assert converter.tikz_dir.exists()
        assert converter.tikz_dir.is_dir()
    
    def test_extract_counts_figures(self, sample_tikz_tex):
        """Test that extraction counts TikZ figures correctly."""
        converter = TexConverter(sample_tikz_tex)
        count = converter.extract_tikz()
        
        assert count == 2  # sample_tikz_tex has 2 figures
    
    def test_extract_creates_tex_files(self, sample_tikz_tex):
        """Test that extraction creates standalone TeX files."""
        converter = TexConverter(sample_tikz_tex)
        converter.extract_tikz()
        
        tex_files = list(converter.tikz_dir.glob('*.tex'))
        assert len(tex_files) == 2


class TestCleanup:
    """Test cleanup functionality."""
    
    def test_cleanup_removes_directories(self, sample_tex_file):
        """Test that cleanup removes temporary directories."""
        converter = TexConverter(sample_tex_file)
        converter.extract_tikz()
        
        assert converter.tikz_dir.exists()
        assert converter.png_dir.exists()
        
        converter.cleanup()
        
        assert not converter.tikz_dir.exists()
        assert not converter.png_dir.exists()
    
    def test_cleanup_removes_intermediate_files(self, sample_tex_file):
        """Test that cleanup removes intermediate TeX files."""
        converter = TexConverter(sample_tex_file)
        converter.preprocess_tex()
        
        assert converter.pandoc_path.exists()
        
        converter.cleanup()
        
        assert not converter.pandoc_path.exists()
