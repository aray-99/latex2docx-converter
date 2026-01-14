#!/usr/bin/env python3
"""
TikZ図をincludegraphicsで置換するスクリプト（自動ラベル検出対応）
"""

import re
import sys


def auto_detect_tikz_labels(tex_file):
    """TeXファイルから \label{fig:...} を自動検出"""
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'\\label\{fig:([^}]+)\}'
    matches = re.findall(pattern, content)
    return matches


def replace_tikz_with_images(input_file, output_file, png_dir='tikz_png', labels=None):
    """
    TikZ図をPNG画像への参照で置換
    
    Args:
        input_file: 入力TeX ファイル
        output_file: 出力TeX ファイル
        png_dir: PNG画像ディレクトリ
        labels: ラベル名リスト（Noneの場合は自動検出）
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ラベルを自動検出（提供されない場合）
    if labels is None:
        labels = auto_detect_tikz_labels(input_file)
    
    # TikZ図を検索して置換
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
        # center環境で画像を挿入
        return f'\\begin{{center}}\n\\includegraphics[width=0.8\\textwidth]{{{png_filename}}}\n\\end{{center}}'
    
    new_content = re.sub(tikz_pattern, replace_func, content, flags=re.DOTALL)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"=== {counter} 個のTikZ図を画像参照に置換しました ===")
    print(f"出力ファイル: {output_file}")


if __name__ == '__main__':
    # コマンドライン引数でファイル指定
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
