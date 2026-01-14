#!/bin/bash
# TikZ図をコンパイルしてPNG化するスクリプト（labelベース版）

TIKZ_DIR="tikz_extracted"
PNG_DIR="tikz_png"

# PNGディレクトリをクリーン
if [ -d "$PNG_DIR" ]; then
    echo "=== PNGディレクトリをクリーン ==="
    rm -rf "$PNG_DIR"
fi
mkdir -p "$PNG_DIR"

echo "=== TikZ図をPDFに変換 ==="
cd "$TIKZ_DIR"

for tex_file in *.tex; do
    echo "コンパイル中: $tex_file"
    pdflatex -interaction=nonstopmode "$tex_file" > /dev/null 2>&1
    
    if [ -f "${tex_file%.tex}.pdf" ]; then
        echo "  ✓ PDF生成成功: ${tex_file%.tex}.pdf"
    else
        echo "  ✗ PDF生成失敗: $tex_file"
    fi
done

echo ""
echo "=== PDFをPNGに変換 (300dpi) ==="
for pdf_file in *.pdf; do
    png_file="../$PNG_DIR/${pdf_file%.pdf}.png"
    echo "変換中: $pdf_file → $png_file"
    convert -density 300 "$pdf_file" -quality 90 "$png_file" 2>/dev/null
    
    if [ -f "$png_file" ]; then
        echo "  ✓ PNG生成成功"
    else
        echo "  ✗ PNG生成失敗"
    fi
done

cd ..
echo ""
echo "=== 完了 ==="
echo "PNG画像: $PNG_DIR/"
ls -lh "$PNG_DIR"/*.png 2>/dev/null || echo "PNG画像が生成されませんでした"
