#!/usr/bin/env python3
"""
TeXファイルをpandoc変換用に前処理するスクリプト (v3)
アプローチ: \ab(...)のパターンを正規表現で直接置換
"""

import re

def replace_ab_brackets(content):
    """
    \ab(...) を \left(...\right) に置換
    \ab|...| を \left|...\right| に置換
    \ab{...} を \left\{...\right\} に置換
    内側から外側へ段階的に処理することでネストに対応
    """
    max_iterations = 50
    for iteration in range(max_iterations):
        old_content = content
        
        # まず最も単純なケース（中に括弧が全くない）
        pattern_no_parens = r'\\ab\(([^()]+)\)'
        content = re.sub(pattern_no_parens, r'\\left(\1\\right)', content)
        
        # 通常の括弧()を含むケース（\ab(で始まり)で終わる）
        # 中身に\left...\rightがあってもOK
        # (?:[^()]|\([^()]*\)) = 括弧なし文字 or (括弧なし文字)
        pattern_with_parens = r'\\ab\(((?:[^()]|\([^()]*\))+)\)'
        content = re.sub(pattern_with_parens, r'\\left(\1\\right)', content)
        
        # より複雑なネスト（\leftや\rightを含む）
        # \ab(... \left(...\right) ...) のようなケース
        pattern_complex = r'\\ab\(((?:[^()]|\\left[^)]*\\right|\([^()]*\))+)\)'
        try:
            content = re.sub(pattern_complex, r'\\left(\1\\right)', content)
        except:
            pass
        
        # \ab|...| パターン
        content = re.sub(r'\\ab\|([^|]+)\|', r'\\left|\1\\right|', content)
        
        # \ab\{...\} パターン（中に{}がある場合も対応）
        content = re.sub(r'\\ab\\{(.+?)\\}', r'\\left\\{\1\\right\\}', content)
        
        if content == old_content:
            break
    
    return content, iteration + 1

def process_tex_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== Step 1: \\ab() を \\left(...\\right) に置換 ===")
    content, iterations = replace_ab_brackets(content)
    print(f"  置換パス回数: {iterations}")
    
    print("=== Step 2: プリアンブルを簡略化 ===")
    # physics2関連を削除
    content = re.sub(r'\\usepackage\{physics2\}\n?', '', content)
    content = re.sub(r'\\usephysicsmodule\{ab,xmat\}\n?', '', content)
    
    # tikzexternalを無効化
    content = re.sub(r'\\tikzexternalize.*\n?', '', content)
    
    # jlreqをarticleに
    content = re.sub(r'\\documentclass\[lualatex\]\{jlreq\}', r'\\documentclass{article}', content)
    content = re.sub(r'\\usepackage\{luatexja\}\n?', '', content)
    content = re.sub(r'\\ModifyHeading.*\n?', '', content)
    
    print("=== Step 3: カスタムコマンドを展開 ===")
    # \daggnum{X} を (X)-dagger に置換
    content = re.sub(r'\\tag\*\{\\daggnum\{([^}]+)\}\}', r'\\tag{(\1)-dagger}', content)
    
    # \newcommand{\daggnum}... の行を削除
    content = re.sub(r'\\newcommand\{\\daggnum\}.*\n?', '', content)
    
    # ${(X)}^\prime$ のようなパターンを (X)-prime に
    content = re.sub(r'\\tag\*\{\$\{(\([^)]+\))\}\^\\prime\$\}', r'\\tag{\1-prime}', content)
    content = re.sub(r'\\tag\*\{\$\{(\([^)]+\))\}\^\\dagger\$\}', r'\\tag{\1-dagger}', content)
    
    print("=== Step 4: ファイルに書き込み ===")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 統計情報
    tikz_count = len(re.findall(r'\\begin\{tikzpicture\}', content))
    left_count = len(re.findall(r'\\left\(', content))
    right_count = len(re.findall(r'\\right\)', content))
    
    print(f"TikZ図の数: {tikz_count}")
    print(f"\\left( の数: {left_count}")
    print(f"\\right) の数: {right_count}")
    
    if left_count != right_count:
        print(f"⚠ 警告: \\left(と\\right)の数が一致しません（差: {abs(left_count - right_count)}）")
    
    print(f"出力ファイル: {output_file}")
    print("\n=== 前処理完了 ===")

if __name__ == "__main__":
    process_tex_file("main.tex", "main_pandoc.tex")
