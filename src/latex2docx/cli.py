"""
Command-line interface for LaTeX to DOCX converter.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from latex2docx.converter import TexConverter


class CleanupTool:
    """Cleanup utility."""
    
    @staticmethod
    def run() -> int:
        """Clean up generated files."""
        print("Cleaning up generated files...")
        print("")
        
        import shutil
        from glob import glob
        
        cleanup_dirs = ['tikz_extracted', 'tikz_png']
        cleanup_patterns = [
            '*_pandoc.tex',
            '*_with_images.tex',
            '*.docx',
            'compile.log',
            'pandoc_conversion.log'
        ]
        
        # Remove directories
        for dir_name in cleanup_dirs:
            if Path(dir_name).exists():
                print(f"Removing: {dir_name}/")
                shutil.rmtree(dir_name)
        
        # Remove files
        for pattern in cleanup_patterns:
            for file_path in glob(pattern):
                if Path(file_path).is_file():
                    print(f"Removing: {file_path}")
                    Path(file_path).unlink()
        
        print("")
        print("Cleanup complete")
        return 0


def main(argv: Optional[list] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog='latex2docx',
        description='Convert LaTeX to DOCX with integrated TikZ support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  latex2docx main.tex
  latex2docx main.tex output.docx
  latex2docx main.tex --clean
  latex2docx --clean-only
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
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args(argv)
    
    # Cleanup only mode
    if args.clean_only:
        return CleanupTool.run()
    
    # Conversion mode
    if not args.input_file:
        parser.print_help()
        return 1
    
    try:
        converter = TexConverter(
            args.input_file,
            args.output_file,
            verbose=args.verbose,
            clean=args.clean
        )
        return converter.run()
    
    except KeyboardInterrupt:
        print('\nCancelled by user')
        return 130
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
