#!/usr/bin/env python3
r"""
Unified Python script for LaTeX to DOCX conversion pipeline.
Integrates all shell script functionality into a single Python module.

Pipeline:
  1. Preprocess TeX file (bracket replacement)
  2. Extract TikZ figures (auto-label detection)
  3. Compile TikZ to PDF → PNG
  4. Replace TikZ with image references
  5. Convert to DOCX using pandoc
  6. Cleanup (optional)
"""

import os
import sys
import re
import shutil
import subprocess
import argparse
from datetime import datetime
from pathlib import Path


class TexConverter:
    """Main class for LaTeX to DOCX conversion."""
    
    def __init__(self, input_file, output_file=None, verbose=False, clean=False):
        """
        Initialize converter.
        
        Args:
            input_file: Input LaTeX file (relative or absolute path)
            output_file: Output DOCX file (auto-generated if None)
            verbose: Enable verbose output
            clean: Clean up intermediate files after conversion
        """
        self.input_file = input_file
        self.verbose = verbose
        self.clean_after = clean
        
        # Generate output filename if not provided
        if output_file:
            self.output_file = output_file
        else:
            base_name = os.path.splitext(input_file)[0]
            date_str = datetime.now().strftime('%Y%m%d')
            self.output_file = f'output_{date_str}.docx'
        
        # Derived filenames
        self.base_name = os.path.splitext(self.input_file)[0]
        self.pandoc_file = f'{self.base_name}_pandoc.tex'
        self.images_file = f'{self.base_name}_with_images.tex'
        self.tikz_dir = 'tikz_extracted'
        self.png_dir = 'tikz_png'
        
        self._print_header()
    
    def _print(self, message):
        """Print message with optional verbosity control."""
        print(message)
    
    def _print_header(self):
        """Print conversion header."""
        self._print("=" * 50)
        self._print("  LaTeX to DOCX Conversion Pipeline")
        self._print("=" * 50)
        self._print(f"Input file:  {self.input_file}")
        self._print(f"Output file: {self.output_file}")
        self._print("")
    
    def _step_header(self, step_num, step_name):
        """Print step header."""
        self._print(f"\n[{step_num}/5] {step_name}")
    
    def preprocess_tex(self):
        """Step 1: Preprocess TeX file (bracket replacement)."""
        self._step_header(1, "Preprocessing TeX file")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
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
        content = re.sub(r'\\tag\*\{\$\{(\([^)]+\))\}\^\\prime\$\}', 
                        r'\\tag{\1-prime}', content)
        content = re.sub(r'\\tag\*\{\$\{(\([^)]+\))\}\^\\dagger\$\}', 
                        r'\\tag{\1-dagger}', content)
        
        # Write output
        with open(self.pandoc_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Print statistics
        tikz_count = len(re.findall(r'\\begin\{tikzpicture\}', content))
        left_count = len(re.findall(r'\\left\(', content))
        right_count = len(re.findall(r'\\right\)', content))
        
        self._print(f"  TikZ figures: {tikz_count}")
        self._print(f"  \\left( count: {left_count}")
        self._print(f"  \\right) count: {right_count}")
        
        if left_count != right_count:
            self._print(f"  Warning: \\left( and \\right) mismatch")
        
        self._print(f"  Output: {self.pandoc_file}")
    
    @staticmethod
    def _replace_ab_brackets(content):
        """Replace \\ab(...) with \\left(...\\right)."""
        max_iterations = 50
        for iteration in range(max_iterations):
            old_content = content
            
            # Case 1: No parentheses inside
            pattern_no_parens = r'\\ab\(([^()]+)\)'
            content = re.sub(pattern_no_parens, r'\\left(\1\\right)', content)
            
            # Case 2: With parentheses
            pattern_with_parens = r'\\ab\(((?:[^()]|\([^()]*\))+)\)'
            content = re.sub(pattern_with_parens, r'\\left(\1\\right)', content)
            
            # Case 3: Complex nesting
            pattern_complex = r'\\ab\(((?:[^()]|\\left[^)]*\\right|\([^()]*\))+)\)'
            try:
                content = re.sub(pattern_complex, r'\\left(\1\\right)', content)
            except:
                pass
            
            # Handle \ab|...| pattern
            content = re.sub(r'\\ab\|([^|]+)\|', r'\\left|\1\\right|', content)
            
            # Handle \ab\{...\} pattern
            content = re.sub(r'\\ab\\{(.+?)\\}', r'\\left\\{\1\\right\\}', content)
            
            if content == old_content:
                break
        
        return content, iteration + 1
    
    def extract_tikz(self):
        """Step 2: Extract TikZ figures."""
        self._step_header(2, "Extracting TikZ figures")
        
        # Clean and create directories
        if os.path.exists(self.tikz_dir):
            shutil.rmtree(self.tikz_dir)
        if os.path.exists(self.png_dir):
            shutil.rmtree(self.png_dir)
        
        os.makedirs(self.tikz_dir, exist_ok=True)
        os.makedirs(self.png_dir, exist_ok=True)
        
        # Copy data directory if exists
        if os.path.exists('data') and not os.path.exists(
            os.path.join(self.tikz_dir, 'data')):
            shutil.copytree('data', os.path.join(self.tikz_dir, 'data'))
            self._print("  Copied data directory")
        
        # Read input file
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract TikZ figures
        tikz_pattern = r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}'
        tikz_figures = re.findall(tikz_pattern, content, re.DOTALL)
        
        # Auto-detect labels
        labels = self._extract_tikz_labels(content)
        
        self._print(f"  Detected {len(tikz_figures)} TikZ figures")
        self._print(f"  Detected {len(labels)} labels")
        self._print("")
        
        # Save each TikZ figure
        for i, tikz_code in enumerate(tikz_figures, 1):
            if i <= len(labels):
                label_name = list(labels.keys())[i - 1]
            else:
                label_name = f'tikz-{i:02d}'
            
            standalone_content = f"""\\documentclass{{standalone}}
\\usepackage{{tikz}}
\\usetikzlibrary{{calc,positioning,patterns,arrows.meta,decorations.pathmorphing}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}
\\usepackage{{amsmath,amssymb,bm,siunitx}}

\\begin{{document}}
{tikz_code}
\\end{{document}}
"""
            
            output_file = os.path.join(self.tikz_dir, f'{label_name}.tex')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(standalone_content)
            
            self._print(f"  [{i:02d}] {label_name}")
        
        return len(tikz_figures)
    
    @staticmethod
    def _extract_tikz_labels(tex_content):
        """Auto-detect \\label{fig:...} from LaTeX file."""
        pattern = r'\\label\{fig:([^}]+)\}'
        matches = re.finditer(pattern, tex_content)
        
        labels = {}
        for match in matches:
            label_name = match.group(1)
            labels[label_name] = label_name
        
        return labels
    
    def compile_tikz(self):
        """Step 3: Compile TikZ figures to PNG."""
        self._step_header(3, "Compiling TikZ to PDF → PNG")
        
        # Change to tikz_extracted directory
        original_dir = os.getcwd()
        os.chdir(self.tikz_dir)
        
        try:
            # Compile to PDF
            self._print("  Compiling to PDF:")
            for tex_file in sorted(os.listdir('.')):
                if not tex_file.endswith('.tex'):
                    continue
                
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', tex_file],
                    capture_output=True, text=True
                )
                
                pdf_file = tex_file.replace('.tex', '.pdf')
                if os.path.exists(pdf_file):
                    self._print(f"    ✓ {pdf_file}")
                else:
                    self._print(f"    ✗ Failed: {tex_file}")
            
            # Convert to PNG
            self._print("  Converting to PNG (300 DPI):")
            png_count = 0
            for pdf_file in sorted(os.listdir('.')):
                if not pdf_file.endswith('.pdf'):
                    continue
                
                png_name = pdf_file.replace('.pdf', '.png')
                png_path = os.path.join('..', self.png_dir, png_name)
                
                result = subprocess.run(
                    ['convert', '-density', '300', pdf_file, 
                     '-quality', '90', png_path],
                    capture_output=True, text=True
                )
                
                if os.path.exists(png_path):
                    self._print(f"    ✓ {png_name}")
                    png_count += 1
                else:
                    self._print(f"    ✗ Failed: {pdf_file}")
            
            self._print(f"  Generated {png_count} PNG images")
        
        finally:
            os.chdir(original_dir)
    
    def replace_tikz(self):
        """Step 4: Replace TikZ with image references."""
        self._step_header(4, "Replacing TikZ with images")
        
        with open(self.pandoc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Auto-detect labels
        labels = self._extract_tikz_labels(content)
        label_list = list(labels.keys())
        
        # Replace TikZ figures
        tikz_pattern = r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}'
        counter = [0]
        
        def replace_func(match):
            label_name = (label_list[counter[0]] 
                         if counter[0] < len(label_list) 
                         else f'tikz-{counter[0]:02d}')
            counter[0] += 1
            png_filename = f'{self.png_dir}/{label_name}.png'
            return (f'\\begin{{center}}\n'
                   f'\\includegraphics[width=0.8\\textwidth]{{{png_filename}}}\n'
                   f'\\end{{center}}')
        
        new_content = re.sub(tikz_pattern, replace_func, content, 
                            flags=re.DOTALL)
        
        with open(self.images_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        self._print(f"  Replaced {counter[0]} TikZ figures")
        self._print(f"  Output: {self.images_file}")
    
    def convert_to_docx(self):
        """Step 5: Convert to DOCX using pandoc."""
        self._step_header(5, "Converting to DOCX")
        
        self._print("  Running pandoc with options:")
        self._print("    - Number sections")
        self._print("    - Table of contents")
        self._print("    - Standalone document")
        
        pandoc_cmd = [
            'pandoc', self.images_file, '-o', self.output_file,
            '--resource-path=.:tikz_png:data:figures',
            '--number-sections',
            '--toc',
            '--standalone'
        ]
        
        with open('pandoc_conversion.log', 'w') as log:
            result = subprocess.run(pandoc_cmd, stdout=log, stderr=log)
        
        if result.returncode == 0 and os.path.exists(self.output_file):
            file_size = os.path.getsize(self.output_file)
            file_size_mb = file_size / (1024 * 1024)
            self._print(f"  ✓ Conversion successful")
            self._print(f"    Output: {self.output_file} ({file_size_mb:.2f} MB)")
        else:
            raise RuntimeError("Pandoc conversion failed. Check pandoc_conversion.log")
    
    def cleanup(self):
        """Clean up intermediate files."""
        cleanup_dirs = [self.tikz_dir, self.png_dir]
        cleanup_files = [
            self.pandoc_file,
            self.images_file,
            'compile.log',
            'pandoc_conversion.log'
        ]
        
        self._print("\nCleaning up intermediate files:")
        
        for dir_name in cleanup_dirs:
            if os.path.exists(dir_name):
                self._print(f"  Removing {dir_name}/")
                shutil.rmtree(dir_name)
        
        for file_name in cleanup_files:
            if os.path.exists(file_name):
                self._print(f"  Removing {file_name}")
                os.remove(file_name)
    
    def run(self):
        """Execute complete conversion pipeline."""
        try:
            # Check input file exists
            if not os.path.exists(self.input_file):
                raise FileNotFoundError(f"Input file not found: {self.input_file}")
            
            # Execute pipeline
            self.preprocess_tex()
            self.extract_tikz()
            self.compile_tikz()
            self.replace_tikz()
            self.convert_to_docx()
            
            # Cleanup if requested
            if self.clean_after:
                self.cleanup()
            
            # Print completion message
            self._print("\n" + "=" * 50)
            self._print("  Conversion Complete")
            self._print("=" * 50)
            self._print(f"\nOutput: {self.output_file}")
            if os.path.exists(self.output_file):
                file_size = os.path.getsize(self.output_file)
                self._print(f"Size: {file_size:,} bytes\n")
            
            return 0
        
        except Exception as e:
            self._print(f"\nError: {str(e)}")
            return 1


class CleanupTool:
    """Tool for cleaning up generated files."""
    
    @staticmethod
    def run(verbose=False):
        """Clean up generated files."""
        print("Cleaning up generated files...")
        print("")
        
        cleanup_dirs = [
            'tikz_extracted',
            'tikz_png'
        ]
        
        cleanup_patterns = [
            '*_pandoc.tex',
            '*_with_images.tex',
            '*.docx',
            'compile.log',
            'pandoc_conversion.log'
        ]
        
        # Remove directories
        for dir_name in cleanup_dirs:
            if os.path.exists(dir_name):
                print(f"Removing: {dir_name}/")
                shutil.rmtree(dir_name)
        
        # Remove files
        from glob import glob
        for pattern in cleanup_patterns:
            for file_path in glob(pattern):
                if os.path.isfile(file_path):
                    print(f"Removing: {file_path}")
                    os.remove(file_path)
        
        print("")
        print("Cleanup complete")
        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert LaTeX to DOCX with integrated TikZ support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 convert_latex_to_docx.py main.tex
  python3 convert_latex_to_docx.py main.tex output.docx
  python3 convert_latex_to_docx.py main.tex --clean
  python3 convert_latex_to_docx.py --clean-only
        '''
    )
    
    parser.add_argument(
        'input_file',
        nargs='?',
        help='Input LaTeX file'
    )
    
    parser.add_argument(
        'output_file',
        nargs='?',
        help='Output DOCX file (auto-generated if not specified)'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean up intermediate files after conversion'
    )
    
    parser.add_argument(
        '--clean-only',
        action='store_true',
        help='Only cleanup intermediate files (do not convert)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Cleanup only mode
    if args.clean_only:
        return CleanupTool.run(args.verbose)
    
    # Conversion mode
    if not args.input_file:
        parser.print_help()
        return 1
    
    converter = TexConverter(
        args.input_file,
        args.output_file,
        verbose=args.verbose,
        clean=args.clean
    )
    
    return converter.run()


if __name__ == '__main__':
    sys.exit(main())
