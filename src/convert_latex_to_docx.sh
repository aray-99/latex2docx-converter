#!/bin/bash
# pandoc変換の全プロセスを自動化するスクリプト

# コマンドライン引数でファイル指定
INPUT_FILE="${1:-main.tex}"
OUTPUT_FILE="${2:-}"

# 出力ファイル名が指定されない場合は自動生成
if [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_DATE=$(date +%Y%m%d)
    OUTPUT_FILE="output_${OUTPUT_DATE}.docx"
fi

# ファイルの基本名（拡張子なし）
BASE_NAME="${INPUT_FILE%.tex}"
PANDOC_FILE="${BASE_NAME}_pandoc.tex"
IMAGES_FILE="${BASE_NAME}_with_images.tex"

echo "=============================================="
echo "  LaTeX to DOCX 変換プロセス"
echo "=============================================="
echo "入力ファイル: $INPUT_FILE"
echo "出力ファイル: $OUTPUT_FILE"
echo ""

# Step 1: TeXファイルの前処理
echo "[1/5] TeXファイルの前処理（括弧置換）"
python3 preprocess.py "$INPUT_FILE" "$PANDOC_FILE"
if [ $? -ne 0 ]; then
    echo "エラー: 前処理に失敗しました"
    exit 1
fi
echo ""

# Step 2: TikZ図の抽出（dataディレクトリもコピー）
echo "[2/5] TikZ図の抽出（自動ラベル検出）"
python3 extract_tikz_improved.py "$INPUT_FILE"
if [ $? -ne 0 ]; then
    echo "エラー: TikZ図の抽出に失敗しました"
    exit 1
fi
echo ""

# Step 3: TikZ図のコンパイル
echo "[3/5] TikZ図のコンパイル（PDF → PNG）"
./compile_tikz_labeled.sh > compile.log 2>&1
if [ $? -ne 0 ]; then
    echo "エラー: TikZ図のコンパイルに失敗しました"
    echo "詳細: compile.log を確認してください"
    exit 1
fi

# PNG画像の確認
echo "  生成されたPNG画像:"
for png in tikz_png/*.png; do
    [ -f "$png" ] && echo "    - $(basename $png)"
done
echo ""

# Step 4: TikZ図を画像参照に置換
echo "[4/5] TikZ図を画像参照に置換"
python3 replace_tikz_labeled.py "$PANDOC_FILE" "$IMAGES_FILE"
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

pandoc "$IMAGES_FILE" -o "${OUTPUT_FILE}" \
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
[ -d tikz_png ] && ls -1 tikz_png/*.png 2>/dev/null | sed 's/^/  - /' || echo "  (なし)"
echo "  - pandoc_conversion.log (pandoc変換)"

