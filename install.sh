#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Checking ecommerce-viral-remix-workflow dependencies..."

if ! command -v uv >/dev/null 2>&1; then
  echo "Missing uv. Install: brew install uv"
  exit 1
fi

if ! command -v yt-dlp >/dev/null 2>&1; then
  echo "Missing yt-dlp. Install: brew install yt-dlp"
  exit 1
fi

if [[ -z "${GEMINI_API_KEY:-}" && -z "${GOOGLE_API_KEY:-}" && -z "${CUSTOM_API_KEY:-}" ]]; then
  echo "Warning: no API key found. Set GEMINI_API_KEY/GOOGLE_API_KEY, or CUSTOM_API_KEY with CUSTOM_BASE_URL/CUSTOM_MODEL, unless using --prompt-only."
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Warning: ffmpeg not found. Custom provider video analysis needs it for keyframe extraction: brew install ffmpeg"
fi

chmod +x "$SKILL_DIR"/scripts/*.py

echo "OK. Try:"
echo "uv run $SKILL_DIR/scripts/run_workflow.py --texts /path/to/article.md --product $SKILL_DIR/templates/example-product-brief.yaml --workdir _temp/example-case"
