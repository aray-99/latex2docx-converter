"""
Core converter module with LaTeX to DOCX pipeline.
"""

import logging
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class TexConverter:
    """Modern LaTeX to DOCX converter."""
    
    def __init__(
        self,
        input_file: str | Path,
        output_file: Optional[str | Path] = None,
        verbose: bool = False,
        clean: bool = False,
    ):
        """
        Initialize converter.
        
        Args:
            input_file: Input LaTeX file
            output_file: Output DOCX file (auto-generated if None)
            verbose: Enable verbose logging
            clean: Clean intermediate files after conversion
        """
        self.input_path = Path(input_file)
        self.verbose = verbose
        self.clean_after = clean
        
        # Setup logging
        self._setup_logging()
        
        # Validate input file
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")
        
        # Generate output filename
        if output_file:
            self.output_path = Path(output_file)
        else:
            date_str = datetime.now().strftime('%Y%m%d')
            stem = self.input_path.stem
            self.output_path = Path(f'output_{date_str}.docx')
        
        # Derived paths
        self.stem = self.input_path.stem
        self.pandoc_path = self.input_path.parent / f'{self.stem}_pandoc.tex'
        self.images_path = self.input_path.parent / f'{self.stem}_with_images.tex'
        self.tikz_dir = self.input_path.parent / 'tikz_extracted'
        self.png_dir = self.input_path.parent / 'tikz_png'
        
        self._print_header()
    
    def _setup_logging(self):
        """Configure logging."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(message)s'
        )
    
    def _print(self, message: str, level: str = 'info'):
        """Log message."""
        if level == 'debug':
            logger.debug(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)
        else:
            logger.info(message)
    
    def _print_header(self):
        """Print conversion header."""
        self._print("=" * 50)
        self._print("  LaTeX to DOCX Conversion Pipeline")
        self._print("=" * 50)
        self._print(f"Input file:  {self.input_path}")
        self._print(f"Output file: {self.output_path}")
        self._print("")
    
    def _step(self, step_num: int, step_name: str):
        """Log step."""
        self._print(f"\n[{step_num}/5] {step_name}")
    
    def preprocess_tex(self) -> None:
        """Step 1: Preprocess TeX file."""
        self._step(1, "Preprocessing TeX file")
        
        content = self.input_path.read_text(encoding='utf-8')
        
        # Replace \ab(...) with \left(...\right)
        self._print("  Converting \\ab() to \\left(...\\right)")
        content, iterations = self._replace_ab_brackets(content)
        self._print(f"    Replacement passes: {iterations}")
        
        # Simplify preamble
        self._print("  Simplifying preamble")
        content = re.sub(r'\\usepackage\{physics2\}\n?', '', content)
        content = re.sub(r'\\usephysicsmodule\{ab,xmat\}\n?', '', content)
        content = re.sub(r'\\tikzexternalize.*\n?', '', content)
        content = re.sub(r'\\documentclass\[lualatex\]\{jlreq\}',
                        r'\\documentclass{article}', content)
        content = re.sub(r'\\usepackage\{luatexja\}\n?', '', content)
        content = re.sub(r'\\ModifyHeading.*\n?', '', content)
        
        # Expand custom commands
        self._print("  Expanding custom commands")
        content = re.sub(r'\\tag\*\{\\daggnum\{([^}]+)\}\}',
                        r'\\tag{(\1)-dagger}', content)
        content = re.sub(r'\\newcommand\{\\daggnum\}.*\n?', '', content)
        
        # Write output
        self.pandoc_path.write_text(content, encoding='utf-8')
        
        # Print statistics
        tikz_count = len(re.findall(r'\\begin\{tikzpicture\}', content))
        left_count = len(re.findall(r'\\left\(', content))
        right_count = len(re.findall(r'\\right\)', content))
        
        self._print(f"  TikZ figures: {tikz_count}")
        self._print(f"  \\left( / \\right): {left_count} / {right_count}")
        self._print(f"  Output: {self.pandoc_path.name}")
    
    @staticmethod
    def _replace_ab_brackets(content: str) -> Tuple[str, int]:
        """Replace \\ab(...) with \\left(...\\right)."""
        max_iterations = 50
        for iteration in range(max_iterations):
            old_content = content
            
            # Case 1: No parentheses inside
            pattern = r'\\ab\(([^()]+)\)'
            content = re.sub(pattern, r'\\left(\1\\right)', content)
            
            # Case 2: With parentheses
            pattern = r'\\ab\(((?:[^()]|\([^()]*\))+)\)'
            content = re.sub(pattern, r'\\left(\1\\right)', content)
            
            # Case 3: Complex nesting
            pattern = r'\\ab\(((?:[^()]|\\left[^)]*\\right|\([^()]*\))+)\)'
            try:
                content = re.sub(pattern, r'\\left(\1\\right)', content)
            except Exception:
                pass
            
            # Handle \ab|...| pattern
            content = re.sub(r'\\ab\|([^|]+)\|', r'\\left|\1\\right|', content)
            
            # Handle \ab\{...\} pattern
            content = re.sub(r'\\ab\\{(.+?)\\}', r'\\left\\{\1\\right\\}', content)
            
            if content == old_content:
                break
        
        return content, iteration + 1
    
    def extract_tikz(self) -> int:
        """Step 2: Extract TikZ figures."""
        self._step(2, "Extracting TikZ figures")
        
        # Clean and create directories
        for directory in [self.tikz_dir, self.png_dir]:
            if directory.exists():
                shutil.rmtree(directory)
            directory.mkdir(parents=True, exist_ok=True)
        
        # Copy data directory if exists
        data_dir = self.input_path.parent / 'data'
        if data_dir.exists():
            shutil.copytree(
                data_dir,
                self.tikz_dir / 'data',
                dirs_exist_ok=True
            )
            self._print("  Copied data directory")
        
        # Read input file
        content = self.input_path.read_text(encoding='utf-8')
        
        # Extract TikZ figures
        tikz_pattern = r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}'
        tikz_figures = re.findall(tikz_pattern, content, re.DOTALL)
        
        # Auto-detect labels
        labels = self._extract_labels(content)
        
        self._print(f"  Detected {len(tikz_figures)} TikZ figures")
        self._print(f"  Detected {len(labels)} labels")
        self._print("")
        
        # Save each TikZ figure
        for i, tikz_code in enumerate(tikz_figures, 1):
            label_name = (
                list(labels.keys())[i - 1]
                if i <= len(labels)
                else f'tikz-{i:02d}'
            )
            
            standalone_tex = self._make_standalone_tex(tikz_code)
            output_file = self.tikz_dir / f'{label_name}.tex'
            output_file.write_text(standalone_tex, encoding='utf-8')
            
            self._print(f"  [{i:02d}] {label_name}")
        
        return len(tikz_figures)
    
    @staticmethod
    def _extract_labels(tex_content: str) -> Dict[str, str]:
        """Extract \\label{fig:...} from LaTeX content."""
        pattern = r'\\label\{fig:([^}]+)\}'
        labels = {}
        for match in re.finditer(pattern, tex_content):
            label_name = match.group(1)
            labels[label_name] = label_name
        return labels
    
    @staticmethod
    def _make_standalone_tex(tikz_code: str) -> str:
        """Create standalone TeX document for TikZ figure."""
        return f"""\\documentclass{{standalone}}
\\usepackage{{tikz}}
\\usetikzlibrary{{calc,positioning,patterns,arrows.meta,decorations.pathmorphing}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}
\\usepackage{{amsmath,amssymb,bm,siunitx}}

\\begin{{document}}
{tikz_code}
\\end{{document}}
"""
    
    def compile_tikz(self) -> int:
        """Step 3: Compile TikZ to PDF → PNG."""
        self._step(3, "Compiling TikZ to PDF → PNG")
        
        original_dir = Path.cwd()
        os.chdir(self.tikz_dir)
        
        try:
            # Compile to PDF
            self._print("  Compiling to PDF:")
            pdf_count = 0
            for tex_file in sorted(Path('.').glob('*.tex')):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', str(tex_file.name)],
                    capture_output=True,
                    text=True
                )
                
                pdf_file = tex_file.with_suffix('.pdf')
                if pdf_file.exists():
                    self._print(f"    ✓ {pdf_file.name}")
                    pdf_count += 1
                else:
                    self._print(f"    ✗ Failed: {tex_file.name}", level='warning')
            
            # Convert to PNG
            self._print("  Converting to PNG (300 DPI):")
            png_count = 0
            for pdf_file in sorted(Path('.').glob('*.pdf')):
                png_name = pdf_file.stem + '.png'
                png_path = original_dir / self.png_dir / png_name
                
                result = subprocess.run(
                    ['convert', '-density', '300', str(pdf_file),
                     '-quality', '90', str(png_path)],
                    capture_output=True,
                    text=True
                )
                
                if png_path.exists():
                    self._print(f"    ✓ {png_name}")
                    png_count += 1
                else:
                    self._print(f"    ✗ Failed: {pdf_file.name}", level='warning')
            
            self._print(f"  Generated {png_count} PNG images")
            return png_count
        
        finally:
            os.chdir(original_dir)
    
    def replace_tikz(self) -> None:
        """Step 4: Replace TikZ with images."""
        self._step(4, "Replacing TikZ with images")
        
        content = self.pandoc_path.read_text(encoding='utf-8')
        labels = self._extract_labels(self.input_path.read_text(encoding='utf-8'))
        label_list = list(labels.keys())
        
        # Replace TikZ figures
        tikz_pattern = r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}'
        counter = [0]
        
        def replace_func(match):
            label_name = (
                label_list[counter[0]]
                if counter[0] < len(label_list)
                else f'tikz-{counter[0]:02d}'
            )
            counter[0] += 1
            png_filename = f'tikz_png/{label_name}.png'
            return (
                f'\\begin{{center}}\n'
                f'\\includegraphics[width=0.8\\textwidth]{{{png_filename}}}\n'
                f'\\end{{center}}'
            )
        
        new_content = re.sub(tikz_pattern, replace_func, content, flags=re.DOTALL)
        self.images_path.write_text(new_content, encoding='utf-8')
        
        self._print(f"  Replaced {counter[0]} TikZ figures")
        self._print(f"  Output: {self.images_path.name}")
    
    def convert_to_docx(self) -> None:
        """Step 5: Convert to DOCX."""
        self._step(5, "Converting to DOCX")
        
        self._print("  Running pandoc with options:")
        self._print("    - Number sections")
        self._print("    - Table of contents")
        self._print("    - Standalone document")
        
        cmd = [
            'pandoc', str(self.images_path), '-o', str(self.output_path),
            f'--resource-path={self.input_path.parent}:tikz_png:data:figures',
            '--number-sections',
            '--toc',
            '--standalone'
        ]
        
        log_file = self.input_path.parent / 'pandoc_conversion.log'
        with open(log_file, 'w') as log:
            result = subprocess.run(cmd, stdout=log, stderr=log)
        
        if result.returncode == 0 and self.output_path.exists():
            file_size = self.output_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            self._print(f"  ✓ Conversion successful")
            self._print(f"    Output: {self.output_path.name} ({file_size_mb:.2f} MB)")
        else:
            raise RuntimeError("Pandoc conversion failed")
    
    def cleanup(self) -> None:
        """Clean up intermediate files."""
        self._print("\nCleaning up intermediate files:")
        
        for path in [self.tikz_dir, self.png_dir]:
            if path.exists():
                self._print(f"  Removing {path.name}/")
                shutil.rmtree(path)
        
        for file in [self.pandoc_path, self.images_path]:
            if file.exists():
                self._print(f"  Removing {file.name}")
                file.unlink()
        
        for log_file in ['compile.log', 'pandoc_conversion.log']:
            path = self.input_path.parent / log_file
            if path.exists():
                self._print(f"  Removing {log_file}")
                path.unlink()
    
    def run(self) -> int:
        """Execute complete conversion pipeline."""
        try:
            self.preprocess_tex()
            self.extract_tikz()
            self.compile_tikz()
            self.replace_tikz()
            self.convert_to_docx()
            
            if self.clean_after:
                self.cleanup()
            
            # Print completion
            self._print("\n" + "=" * 50)
            self._print("  Conversion Complete")
            self._print("=" * 50)
            self._print(f"\nOutput: {self.output_path}")
            if self.output_path.exists():
                file_size = self.output_path.stat().st_size
                self._print(f"Size: {file_size:,} bytes\n")
            
            return 0
        
        except Exception as e:
            self._print(f"\nError: {str(e)}", level='error')
            return 1
