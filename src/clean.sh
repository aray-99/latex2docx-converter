#!/bin/bash
# LaTeX変換プロセスで生成されたファイルをクリーンアップ

echo "清理を開始します..."
echo ""

# クリーンアップするディレクトリ
CLEANUP_DIRS=(
    "tikz_extracted"
    "tikz_png"
)

# クリーンアップするファイルパターン
CLEANUP_PATTERNS=(
    "*_pandoc.tex"
    "*_with_images.tex"
    "*.docx"
    "*_*.docx"
    "compile.log"
    "pandoc_conversion.log"
)

# ディレクトリの削除
for dir in "${CLEANUP_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "削除: $dir/"
        rm -rf "$dir"
    fi
done

# ファイルの削除
for pattern in "${CLEANUP_PATTERNS[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            echo "削除: $file"
            rm "$file"
        fi
    done
done

echo ""
echo "清理完了"
