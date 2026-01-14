#!/bin/bash
# pandoc変換の全プロセスを自動化するスクリプト

echo "=============================================="
echo "  main.tex → docx 変換プロセス"
echo "=============================================="
echo ""

# Step 1: TeXファイルの前処理
echo "[1/5] TeXファイルの前処理（括弧置換）"
python3 preprocess.py
if [ $? -ne 0 ]; then
    echo "エラー: 前処理に失敗しました"
    exit 1
fi
echo ""

# Step 2: TikZ図の抽出（dataディレクトリもコピー）
echo "[2/5] TikZ図の抽出（labelベース + dataディレクトリコピー）"
python3 extract_tikz_improved.py
if [ $? -ne 0 ]; then
    echo "エラー: TikZ図の抽出に失敗しました"
    exit 1
fi
echo ""

# Step 3: TikZ図のコンパイル
echo "[3/5] TikZ図のコンパイル（PDF → PNG、データプロット含む）"
./compile_tikz_labeled.sh > compile.log 2>&1
if [ $? -ne 0 ]; then
    echo "エラー: TikZ図のコンパイルに失敗しました"
    echo "詳細: compile.log を確認してください"
    exit 1
fi

# PNG画像の確認
echo "  生成されたPNG画像:"
for png in tikz_png/*.png; do
    size=$(identify "$png" 2>/dev/null | awk '{print $3}')
    echo "    - $(basename $png) ($size)"
done
echo ""

# Step 4: TikZ図を画像参照に置換
echo "[4/5] TikZ図を画像参照に置換"
python3 replace_tikz_labeled.py
if [ $? -ne 0 ]; then
    echo "エラー: 画像置換に失敗しました"
    exit 1
fi
echo ""

# Step 5: pandocで最終変換
echo "[5/5] pandocでdocxに変換"
echo "  オプション:"
echo "    - 数式番号・図表番号付き"
echo "    - 目次付き"
echo "    - セクション番号付き"

OUTPUT_DATE=$(date +%Y%m%d)
OUTPUT_FILE="output_${OUTPUT_DATE}.docx"

pandoc main_with_images.tex -o "${OUTPUT_FILE}" \
    --resource-path=.:tikz_png:data:figures \
    --number-sections \
    --toc \
    --standalone \
    2> pandoc_conversion.log

if [ $? -ne 0 ]; then
    echo "エラー: pandoc変換に失敗しました"
    echo "詳細: pandoc_conversion.log を確認してください"
    exit 1
fi

echo "  ✓ 変換完了"
echo ""

# 結果表示
echo "=============================================="
echo "  変換完了"
echo "=============================================="
echo ""
echo "📄 出力ファイル: ${OUTPUT_FILE}"
ls -lh "${OUTPUT_FILE}"
echo ""
echo "📊 生成されたPNG画像:"
ls -1 tikz_png/*.png | sed 's/^/  - /'
echo ""
echo "📝 ログファイル:"
echo "  - compile.log (TikZコンパイル)"
echo "  - pandoc_conversion.log (pandoc変換)"

