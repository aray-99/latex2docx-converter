#!/usr/bin/env python3
r"""
Extract TikZ figures from TeX file and save as standalone files.
Supports automatic label detection.
"""

import re
import os
import shutil
import sys


def extract_tikz_labels(tex_content):
    r"""
    Search for \label{fig:...} in LaTeX file and associate with TikZ figures
    Returns: dictionary {label_name: description}
    """
    # Find \label{fig:...} patterns
    pattern = r'\\label\{fig:([^}]+)\}'
    matches = re.finditer(pattern, tex_content)
    
    labels = {}
    for match in matches:
        label_name = match.group(1)
        labels[label_name] = label_name  # Default: use label_name as is
    
    return labels


def extract_tikz_figures_with_labels(input_file, output_dir='tikz_extracted', 
                                     predefined_labels=None):
    """
    Extract TikZ figures from LaTeX and save as standalone files
    
    Args:
        input_file: Input LaTeX file
        output_dir: Output directory
        predefined_labels: Predefined label dictionary {label_name: description}
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Auto-copy data directory for TikZ compilation
    data_dir = 'data'
    if os.path.exists(data_dir) and not os.path.exists(os.path.join(output_dir, 'data')):
        shutil.copytree(data_dir, os.path.join(output_dir, 'data'))
        print(f"Copied data directory to {output_dir}/")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Search for TikZ figures
    tikz_pattern = r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}'
    tikz_figures = re.findall(tikz_pattern, content, re.DOTALL)
    
    # Auto-detect labels
    auto_labels = extract_tikz_labels(content)
    
    # Merge predefined and auto-detected labels
    if predefined_labels:
        labels = {**auto_labels, **predefined_labels}
    else:
        labels = auto_labels
    
    print(f"\n=== Detected TikZ figures: {len(tikz_figures)} ===")
    print(f"=== Detected labels: {len(labels)} ===\n")
    
    # Save each TikZ figure as a standalone file
    for i, tikz_code in enumerate(tikz_figures, 1):
        # Get label name (list order)
        if i <= len(labels):
            label_name = list(labels.keys())[i - 1]
            description = labels[label_name]
        else:
            label_name = f'tikz-{i:02d}'
            description = f'TikZ Figure {i}'
        
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
        
        output_file = os.path.join(output_dir, f'{label_name}.tex')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(standalone_content)
        
        print(f"[{i:02d}] {output_file}")
        print(f"     {description}")
    
    return len(tikz_figures)


def clean_cache(directories=None):
    """Clean up cache directories"""
    if directories is None:
        directories = ['tikz_extracted', 'tikz_png']
    
    for dir_name in directories:
        if os.path.exists(dir_name):
            print(f"Cleaning: {dir_name}/")
            shutil.rmtree(dir_name)


if __name__ == '__main__':
    # Parse command-line arguments
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        input_file = 'main.tex'
    
    # Clean cache
    clean_cache()
    print()
    
    # Extract TikZ figures
    count = extract_tikz_figures_with_labels(input_file)
    print(f"\n=== Extracted {count} TikZ figures ===")
