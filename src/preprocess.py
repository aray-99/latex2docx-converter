#!/usr/bin/env python3
r"""
TeXファイルをpandoc変換用に前処理するスクリプト (v4)
アプローチ: \\ab(...)のパターンを正規表現で直接置換
"""

import re
import sys

def replace_ab_brackets(content):
    """
    Replace \ab(...) with \left(...\right)
    Replace \ab|...| with \left|...\right|
    Replace \ab{...} with \left\{...\right\}
    Handles nested brackets through iterative processing
    """
    max_iterations = 50
    for iteration in range(max_iterations):
        old_content = content
        
        # Case 1: No parentheses inside
        pattern_no_parens = r'\\ab\(([^()]+)\)'
        content = re.sub(pattern_no_parens, r'\\left(\1\\right)', content)
        
        # Case 2: With parentheses
        pattern_with_parens = r'\\ab\(((?:[^()]|\([^()]*\))+)\)'
        content = re.sub(pattern_with_parens, r'\\left(\1\\right)', content)
        
        # Case 3: Complex nesting with \left...\right
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

def process_tex_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== Step 1: Convert \\ab() to \\left(...\\right) ===")
    content, iterations = replace_ab_brackets(content)
    print(f"  Replacement passes: {iterations}")
    
    print("=== Step 2: Simplify preamble ===")
    # Remove physics2-related packages
    content = re.sub(r'\\usepackage\{physics2\}\n?', '', content)
    content = re.sub(r'\\usephysicsmodule\{ab,xmat\}\n?', '', content)
    
    # Disable tikzexternalize
    content = re.sub(r'\\tikzexternalize.*\n?', '', content)
    
    # Replace jlreq with article
    content = re.sub(r'\\documentclass\[lualatex\]\{jlreq\}', r'\\documentclass{article}', content)
    content = re.sub(r'\\usepackage\{luatexja\}\n?', '', content)
    content = re.sub(r'\\ModifyHeading.*\n?', '', content)
    
    print("=== Step 3: Expand custom commands ===")
    # Replace \daggnum{X} with (X)-dagger
    content = re.sub(r'\\tag\*\{\\daggnum\{([^}]+)\}\}', r'\\tag{(\1)-dagger}', content)
    
    # Remove \newcommand{\daggnum}... lines
    content = re.sub(r'\\newcommand\{\\daggnum\}.*\n?', '', content)
    
    # Replace patterns like ${(X)}^\prime$ with (X)-prime
    content = re.sub(r'\\tag\*\{\$\{(\([^)]+\))\}\^\\prime\$\}', r'\\tag{\1-prime}', content)
    content = re.sub(r'\\tag\*\{\$\{(\([^)]+\))\}\^\\dagger\$\}', r'\\tag{\1-dagger}', content)
    
    print("=== Step 4: Write to output file ===")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Print statistics
    tikz_count = len(re.findall(r'\\begin\{tikzpicture\}', content))
    left_count = len(re.findall(r'\\left\(', content))
    right_count = len(re.findall(r'\\right\)', content))
    
    print(f"TikZ figures: {tikz_count}")
    print(f"\\left( count: {left_count}")
    print(f"\\right) count: {right_count}")
    
    if left_count != right_count:
        print(f"⚠ Warning: \\left( and \\right) count mismatch (difference: {abs(left_count - right_count)})")
    
    print(f"Output file: {output_file}")
    print("\n=== Preprocessing complete ===")

if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    elif len(sys.argv) == 2:
        input_file = sys.argv[1]
        output_file = sys.argv[1].replace('.tex', '_pandoc.tex')
    else:
        input_file = 'main.tex'
        output_file = 'main_pandoc.tex'
    
    process_tex_file(input_file, output_file)
