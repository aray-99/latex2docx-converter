#!/usr/bin/env python3
"""
TikZ図をincludegraphicsで置換するスクリプト（labelベース版）
"""

import re

# TikZ図とそのラベルのマッピング
TIKZ_LABELS = [
    'cantilever-beam',
    'spring-mass-system',
    'model-overview',
    'time-bgs',
    'time-displacement',
    'bgs-displacement-overlay',
    'result-1e-4',
]

def replace_tikz_with_images(input_file, output_file, png_dir='tikz_png'):
    """TikZ図をPNG画像への参照で置換"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # TikZ図を検索して置換
    tikz_pattern = r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}'
    
    counter = 0
    def replace_func(match):
        nonlocal counter
        label_name = TIKZ_LABELS[counter]
        counter += 1
        png_filename = f'{png_dir}/{label_name}.png'
        # center環境で画像を挿入
        return f'\\begin{{center}}\n\\includegraphics[width=0.8\\textwidth]{{{png_filename}}}\n\\end{{center}}'
    
    new_content = re.sub(tikz_pattern, replace_func, content, flags=re.DOTALL)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"=== {counter} 個のTikZ図を画像参照に置換しました ===")
    print(f"出力ファイル: {output_file}")

if __name__ == '__main__':
    # まず前処理版を使用
    input_file = 'main_pandoc.tex'
    output_file = 'main_with_images.tex'
    replace_tikz_with_images(input_file, output_file)
