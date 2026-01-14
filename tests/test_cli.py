"""
Unit tests for CLI interface.

Following TDD principles.
"""

import pytest
from pathlib import Path
from latex2docx.cli import main, CleanupTool


class TestCLIMain:
    """Test CLI main function."""
    
    def test_main_requires_input_file(self):
        """Test that main returns error without input file."""
        result = main([])
        assert result == 1
    
    def test_main_with_help_flag(self):
        """Test that --help returns success."""
        with pytest.raises(SystemExit) as exc_info:
            main(['--help'])
        assert exc_info.value.code == 0
    
    def test_main_with_nonexistent_file(self):
        """Test that main handles non-existent file."""
        result = main(['nonexistent.tex'])
        assert result == 1
    
    def test_main_with_clean_only(self, temp_dir, monkeypatch):
        """Test --clean-only flag."""
        monkeypatch.chdir(temp_dir)
        result = main(['--clean-only'])
        assert result == 0


class TestCleanupTool:
    """Test cleanup utility."""
    
    def test_cleanup_tool_runs(self, temp_dir, monkeypatch):
        """Test that cleanup tool runs successfully."""
        monkeypatch.chdir(temp_dir)
        result = CleanupTool.run()
        assert result == 0
    
    def test_cleanup_removes_tikz_dirs(self, temp_dir, monkeypatch):
        """Test that cleanup removes tikz directories."""
        monkeypatch.chdir(temp_dir)
        
        # Create dummy directories
        (temp_dir / 'tikz_extracted').mkdir()
        (temp_dir / 'tikz_png').mkdir()
        
        CleanupTool.run()
        
        assert not (temp_dir / 'tikz_extracted').exists()
        assert not (temp_dir / 'tikz_png').exists()
