#!/usr/bin/env python3
"""
TeXファイルからTikZ図を抽出して、データパスを修正した上でstandaloneファイルとして保存
"""

import re
import os
import shutil

# TikZ図とそのラベルのマッピング
TIKZ_LABELS = [
    ('cantilever-beam', '片持ち梁の概念図'),
    ('spring-mass-system', 'バネマス系の概念図'),
    ('model-overview', '解析モデルの概要'),
    ('time-bgs', '時間ステップごとのBGS反復回数'),
    ('time-displacement', '時間ステップごとの変位'),
    ('bgs-displacement-overlay', 'BGS反復回数と変位の時間変化（2軸表示）'),
    ('result-1e-4', 'BGS反復回数と変位の時間変化（Δt=1.0e-4）'),
]

def extract_tikz_figures_with_labels(input_file, output_dir='tikz_extracted'):
    """TikZ図を抽出してlabelに基づく名前でstandaloneファイルとして保存"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # dataディレクトリもコピー（TikZ図のコンパイル用）
    if os.path.exists('data') and not os.path.exists(os.path.join(output_dir, 'data')):
        shutil.copytree('data', os.path.join(output_dir, 'data'))
        print(f"dataディレクトリを {output_dir}/ にコピーしました")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # TikZ図を検索
    tikz_pattern = r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}'
    tikz_figures = re.findall(tikz_pattern, content, re.DOTALL)
    
    print(f"\n=== 検出されたTikZ図: {len(tikz_figures)}個 ===\n")
    
    # 各TikZ図をstandaloneファイルとして保存
    for i, (tikz_code, (label_name, description)) in enumerate(zip(tikz_figures, TIKZ_LABELS), 1):
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

def clean_cache():
    """既存のキャッシュディレクトリをクリーン"""
    import shutil
    
    dirs_to_clean = ['tikz_extracted', 'tikz_png']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"クリーニング: {dir_name}/")
            shutil.rmtree(dir_name)

if __name__ == '__main__':
    # キャッシュをクリーン
    clean_cache()
    print()
    
    # TikZ図を抽出
    input_file = 'main.tex'
    count = extract_tikz_figures_with_labels(input_file)
    print(f"\n=== 合計 {count} 個のTikZ図を抽出しました ===")
