#!/usr/bin/env python3
"""
TeXファイルからTikZ図を抽出して、standalone ファイルとして保存
自動ラベル検出対応
"""

import re
import os
import shutil
import sys


def extract_tikz_labels(tex_content):
    r"""
    TeXファイルから \label{fig:...} を検索し、対応するTikZ図を関連付ける
    Returns: {label_name: description} の辞書
    """
    # \label{fig:...} パターンを検索
    pattern = r'\\label\{fig:([^}]+)\}'
    matches = re.finditer(pattern, tex_content)
    
    labels = {}
    for match in matches:
        label_name = match.group(1)
        labels[label_name] = label_name  # デフォルトは label_name をそのまま使用
    
    return labels


def extract_tikz_figures_with_labels(input_file, output_dir='tikz_extracted', 
                                     predefined_labels=None):
    """
    TikZ図を抽出してstandaloneファイルとして保存
    
    Args:
        input_file: 入力TeX ファイル
        output_dir: 出力ディレクトリ
        predefined_labels: 定義済みラベル辞書 {label_name: description}
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    # dataディレクトリもコピー（TikZ図のコンパイル用）
    data_dir = 'data'
    if os.path.exists(data_dir) and not os.path.exists(os.path.join(output_dir, 'data')):
        shutil.copytree(data_dir, os.path.join(output_dir, 'data'))
        print(f"dataディレクトリを {output_dir}/ にコピーしました")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # TikZ図を検索
    tikz_pattern = r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}'
    tikz_figures = re.findall(tikz_pattern, content, re.DOTALL)
    
    # ラベルを自動検出
    auto_labels = extract_tikz_labels(content)
    
    # 定義済みラベルと自動検出ラベルをマージ
    if predefined_labels:
        labels = {**auto_labels, **predefined_labels}
    else:
        labels = auto_labels
    
    print(f"\n=== 検出されたTikZ図: {len(tikz_figures)}個 ===")
    print(f"=== 検出されたラベル: {len(labels)}個 ===\n")
    
    # 各TikZ図をstandaloneファイルとして保存
    for i, tikz_code in enumerate(tikz_figures, 1):
        # ラベル名を取得（リスト順）
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
    """既存のキャッシュディレクトリをクリーン"""
    if directories is None:
        directories = ['tikz_extracted', 'tikz_png']
    
    for dir_name in directories:
        if os.path.exists(dir_name):
            print(f"クリーニング: {dir_name}/")
            shutil.rmtree(dir_name)


if __name__ == '__main__':
    # コマンドライン引数でファイル指定
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        input_file = 'main.tex'
    
    # キャッシュをクリーン
    clean_cache()
    print()
    
    # TikZ図を抽出
    count = extract_tikz_figures_with_labels(input_file)
    print(f"\n=== 合計 {count} 個のTikZ図を抽出しました ===")
