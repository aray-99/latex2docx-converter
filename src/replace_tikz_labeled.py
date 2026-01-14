#!/usr/bin/env python3
r"""
Replace TikZ figures with included graphics (auto-label detection support).
"""

import re
import sys


def auto_detect_tikz_labels(tex_file):
    r"""Auto-detect \label{fig:...} from LaTeX file"""
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'\\label\{fig:([^}]+)\}'
    matches = re.findall(pattern, content)
    return matches


def replace_tikz_with_images(input_file, output_file, png_dir='tikz_png', labels=None):
    r"""
    Replace TikZ environments with \includegraphics commands
    
    Args:
        input_file: Input LaTeX file
        output_file: Output LaTeX file
        png_dir: PNG image directory
        labels: Label name list (auto-detect if None)
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Auto-detect labels if not provided
    if labels is None:
        labels = auto_detect_tikz_labels(input_file)
    
    # Search and replace TikZ figures
    tikz_pattern = r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}'
    
    counter = 0
    def replace_func(match):
        nonlocal counter
        if counter < len(labels):
            label_name = labels[counter]
        else:
            label_name = f'tikz-{counter:02d}'
        counter += 1
        png_filename = f'{png_dir}/{label_name}.png'
        # Insert image in center environment
        return f'\\begin{{center}}\n\\includegraphics[width=0.8\\textwidth]{{{png_filename}}}\n\\end{{center}}'
    
    new_content = re.sub(tikz_pattern, replace_func, content, flags=re.DOTALL)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"=== Replaced {counter} TikZ figures with image references ===")
    print(f"Output file: {output_file}")


if __name__ == '__main__':
    # Parse command-line arguments
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    elif len(sys.argv) == 2:
        input_file = sys.argv[1]
        output_file = sys.argv[1].replace('.tex', '_with_images.tex')
    else:
        input_file = 'main_pandoc.tex'
        output_file = 'main_with_images.tex'
    
    replace_tikz_with_images(input_file, output_file)
